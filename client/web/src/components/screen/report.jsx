import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { ButtonLoading } from "@/components/ui/button-loading"
import { FileDown } from "lucide-react"
import { useClientStore, report, useInsight } from "@/store"
import { useEffect } from "react"
import { useLocation, useParams } from "wouter"

function ReportScreen({}) {
  // const selectedInsight = useClientStore((state) => state.selectedInsight)
  // const workflow_name = useClientStore((state) => state.workflow_name)
  // const taskId = useClientStore((state) => state.taskId)
  // const [wasWorking, setWasWorking] = useState(false)

  const toc = useClientStore((state) => state.toc)
  const updateToc = useClientStore((state) => state.updateToc)
  const comment = useClientStore((state) => state.comment)
  const updateComment = useClientStore((state) => state.updateComment)

  const [, navigate] = useLocation()
  const params = useParams()

  useEffect(() => {
    if (!params || !params.insight_id) {
      console.log("expect /report/[insight_id]")
      navigate("/insights", { replace: true })
    }
  }, [])

  const query = useInsight(params.insight_id)
  const queryClient = useQueryClient()

  const mut = useMutation({
    mutationFn: async (data) => report(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["insight", params.insight_id] })
    },
  })

  function changeToc(e) {
    let lines = e.target.value.split("\n")
    if (lines.length == 1 && lines[0] == "") lines = []
    //    updateToc(lines.filter((l) => l.trim()))
    updateToc(lines)
  }

  function changeComment(e) {
    updateComment(e.target.value)
  }

  function submit(e) {
    mut.mutate({ toc: toc, insight_id: params.insight_id, comment: comment })
  }

  return (
    <>
      <div>
        <h3 className='my-4'>已选择分析结果:</h3>
        {query.data && <div className='bg-slate-100 px-4 py-2 mb-4 text-slate-600 max-w-96 mx-auto'>{query.data.content}</div>}
      </div>
      <div className='grid gap-1.5'>
        <h3 className='my-4'>报告大纲:</h3>
        <Textarea placeholder='' id='outline' rows='10' value={toc.join("\n")} onChange={changeToc} className='max-w-96 mx-auto' />
        <small>首行输入标题,每个纲目或章节单独一行. 首行空白自动生成标题. </small>
        {query.data?.docx && <Input placeholder='修改意见' className='mt-6 max-w-96 mx-auto' value={comment} onChange={changeComment} />}
      </div>
      <div className='my-6 flex flex-col gap-4 w-max mx-auto'>
        {(mut.isPending && <ButtonLoading />) || (
          <Button disabled={toc.length <= 0} onClick={submit}>
            {query.data?.docx ? "再次生成" : "生成"}
          </Button>
        )}
        {!mut.isPending && (
          <Button variant='outline' onClick={() => navigate("/insights")}>
            选择其他分析结果
          </Button>
        )}
      </div>
      {!mut.isPending && query.data?.docx && (
        <div className='grid gap-1.5 max-w-96 border rounded px-4 py-2 pb-6 mx-auto'>
          <p className='my-4'>报告已生成,点击下载</p>
          <p className='bg-slate-100 px-4 py-2 hover:underline flex gap-2 items-center overflow-hidden'>
            <FileDown className='h-4 w-4 text-slate-400' />
            <a className='truncate ' href={`${import.meta.env.VITE_PB_BASE}/api/files/${query.data.collectionName}/${query.data.id}/${query.data.docx}`} target='_blank' rel='noreferrer'>
              {query.data.docx}
            </a>
          </p>
        </div>
      )}
      {query.isError && <p className='text-red-500 my-4'>{query.error.message}</p>}
      {mut.isError && <p className='text-red-500 my-4'>{mut.error.message}</p>}
    </>
  )
}

export default ReportScreen
