#!/usr/bin/env node
import {readFile,lstat,mkdtemp,rm,mkdir,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {canonical,accountName,credential,credentialPath,atomicJson,emit,runBackend,stateHome,platforms,PlatformError,reportError} from '../../platform-runtime/scripts/backend.mjs';

// Import only explicitly supplied API material; validate in a temporary home before replacing a session.
export async function importSession(platform,account,file,backend=runBackend) {
  platform=canonical(platform); account=accountName(account);
  if (!['x','tiktok','weibo'].includes(platform)) throw new PlatformError('USAGE','仅支持 x / tiktok / weibo；快手使用 HTTP 登录');
  const stat=await lstat(file);
  if (!stat.isFile() || stat.isSymbolicLink() || (process.platform!=='win32' && ((stat.mode&0o077)||stat.uid!==process.getuid()))) throw new PlatformError('PRIVATE_FILE_REQUIRED','会话文件必须由当前用户持有，且仅当前用户可读写');
  const data=JSON.parse(await readFile(file,'utf8'));
  if (!data || typeof data!=='object' || !Object.keys(data).length) throw new PlatformError('USAGE','需要有效的 API cookie JSON 文件（Cookie 数组或平台会话对象）');
  await mkdir(stateHome,{recursive:true,mode:0o700});
  const temporary=await mkdtemp(join(stateHome,'session-import-'));
  try {
    await backend(platform,['auth','login','--method','cookie','--cookie','@'+resolve(file),'--account',account],{home:temporary});
    const check=await backend(platform,['auth','status','--account',account],{home:temporary});
    if (!check.data?.logged_in || !check.data.user?.id) throw new PlatformError('AUTH_REQUIRED','会话未通过在线身份校验，旧会话未覆盖',2);
    const saved=await credential(platform,account,temporary);
    if (saved.user?.id!==check.data.user.id) throw new PlatformError('ACCOUNT_MISMATCH','导入与在线校验身份不一致');
    let old;
    try {old=await credential(platform,account);} catch(error) {if(error.code!=='AUTH_REQUIRED')throw error;}
    if (old?.user?.id && old.user.id!==saved.user.id) throw new PlatformError('ACCOUNT_MISMATCH','此账号别名已绑定其他用户，请换用新的 --account');
    const path=credentialPath(platform,account);
    await atomicJson(path,saved);
    const current=join(dirname(path),'_current');
    try {await writeFile(current,account+'\n',{mode:0o600,flag:'wx'});} catch(error){if(error.code!=='EEXIST')throw error;}
    const missing=platform==='tiktok'?platforms.tiktok.write_fields.filter(key=>!saved.device?.[key]):[];
    return {ok:true,platform,account,credential_file:path,write_ready:!missing.length,missing_write_fields:missing};
  } finally {await rm(temporary,{recursive:true,force:true});}
}
if (process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const args=process.argv.slice(2);
  const value=flag=>{const i=args.indexOf(flag);return i>=0?args[i+1]:undefined;};
  try {emit(await importSession(value('--platform'),value('--account')||'default',resolve(value('--file')||'')));}
  catch(error){reportError(error);}
}
