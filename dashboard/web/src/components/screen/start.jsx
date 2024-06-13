import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { ButtonLoading } from "@/components/ui/button-loading"
import { useMutation } from "@tanstack/react-query"
import { Minus, Plus, Loader2 } from "lucide-react"
import { useClientStore, createTask } from "@/store"

function StartScreen({ navigate, id }) {
  const s = useClientStore()
  const mut = useMutation({
    mutationFn: (data) => createTask(data),
    onSuccess: () => {
      //query.invalidate()
      navigate("/articles")
    },
  })

  function change(e) {
    let urls = e.target.value.split("\n")
    if (urls.length == 1 && urls[0] == "") urls = []
    s.setUrls(urls)
  }

  function submit() {
    mut.mutate({ urls: s.urls, days: s.days })
  }

  return (
    <>
      <div className='grid w-full gap-1.5'>
        <Label htmlFor='message'>网站清单</Label>
        <Textarea placeholder='每行输入一个网站的主域名,以http://或https://开头' id='message' rows='20' value={s.urls.join("\n")} onChange={change} />
        {s.countUrls() > 0 && <p className='text-sm text-muted-foreground'>共{s.countUrls()}个网站</p>}
        <div className='my-6 select-none'>
          仅抓取
          <Button variant='outline' size='icon' disabled={s.minDays()} className='mx-2' onClick={s.decr}>
            <Minus className='h-4 w-4' />
          </Button>
          <span className='font-mono'>{s.days}</span>
          <Button variant='outline' size='icon' disabled={s.maxDays()} className='mx-2' onClick={s.incr}>
            <Plus className='h-4 w-4' />
          </Button>
          天内更新的文章
        </div>
      </div>
      {mut.isError && <p className='text-red-500 my-4'>{mut.error.message}</p>}
      {(mut.isPending && <ButtonLoading />) || (
        <Button disabled={s.countUrls() == 0} onClick={submit}>
          {mut.isLoading && <Loader2 className='mr-2 h-4 w-4 animate-spin' />}
          提交
        </Button>
      )}
    </>
  )
}

export default StartScreen
