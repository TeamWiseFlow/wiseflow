import { useEffect } from "react"
import { useLocation } from "wouter"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Files } from "lucide-react"
import { ArticleList } from "@/components/article-list"
import { Button } from "@/components/ui/button"
import { Toaster } from "@/components/ui/toaster"
import { ButtonLoading } from "@/components/ui/button-loading"
import { useToast } from "@/components/ui/use-toast"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { useClientStore, useInsights, unlinkArticle, useInsightDates, useDatePager, more } from "@/store"

function List({ insights, selected, onOpen, onDelete, onReport, onMore, isGettingMore, error }) {
  function change(value) {
    if (value) onOpen(value)
  }

  function unlink(article_id) {
    onDelete(selected, article_id)
  }

  return (
    <Accordion type='single' collapsible onValueChange={change} className='w-full'>
      {insights.map((insight, i) => (
        <AccordionItem value={insight.id} key={i}>
          <AccordionTrigger className='hover:no-underline'>
            <div className='px-4 py-2 cursor-pointer flex items-center gap-2 overflow-hidden'>
              {selected === insight.id && <div className='-ml-4 w-2 h-2 bg-green-400 rounded-full'></div>}
              <p className={"truncate text-wrap text-left flex-1 " + (selected === insight.id ? "font-bold" : "font-normal")}>{insight.content}</p>
              <div className='flex items-center justify-center gap-1'>
                <Files className='h-4 w-4 text-slate-400' />
                <span className='text-slate-400 text-sm leading-none'>x {insight.expand.articles.length}</span>
              </div>
            </div>
          </AccordionTrigger>
          <AccordionContent className='px-4'>
            <ArticleList data={insight.expand.articles} showActions={true} onDelete={unlink} />
            {error && <p className='text-red-500 my-4'>{error.message}</p>}

            {(isGettingMore && <ButtonLoading />) || (
              <div className='flex gap-4 justify-center'>
                <Button onClick={onReport} className='my-4'>
                  生成报告
                </Button>
                <Button variant='outline' onClick={onMore} className='my-4'>
                  搜索更多
                </Button>
              </div>
            )}
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  )
}

function InsightsScreen({}) {
  const selectedInsight = useClientStore((state) => state.selectedInsight)
  const selectInsight = useClientStore((state) => state.selectInsight)
  const dates = useInsightDates()
  const { index, last, next, hasLast, hasNext } = useDatePager(dates)
  // console.log(dates, index)
  const currentDate = dates.length > 0 && index >= 0 ? dates[index] : ""
  const data = useInsights(currentDate)
  // console.log(data)
  const [, navigate] = useLocation()
  const queryClient = useQueryClient()
  const mut = useMutation({
    mutationFn: (params) => {
      if (params && selectedInsight && data.find((insight) => insight.id == selectedInsight).expand.articles.length == 1) {
        throw new Error("不能删除最后一篇文章")
      }
      return unlinkArticle(params)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["insights", currentDate] })
    },
  })

  const mutMore = useMutation({
    mutationFn: (data) => {
      return more(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["insights", currentDate] })
    },
  })

  const { toast } = useToast()
  const queryCache = queryClient.getQueryCache()
  queryCache.onError = (error) => {
    console.log("error in cache", error)
    toast({
      variant: "destructive",
      title: "出错啦！",
      description: error.message,
    })
  }

  useEffect(() => {
    selectInsight(null)
  }, [index])

  useEffect(() => {
    mut.reset() // only show error with the selected insight
  }, [selectedInsight])

  function unlink(insight_id, article_id) {
    mut.mutate({ insight_id, article_id })
  }

  function report() {
    navigate("/report/" + selectedInsight)
  }

  function getMore() {
    console.log()
    mutMore.mutate({ insight_id: selectedInsight })
  }

  return (
    <>
      <h2>分析结果</h2>
      {currentDate && (
        <div className='my-6 flex gap-4 flex items-center'>
          <Button disabled={!hasLast()} variant='outline' onClick={last}>
            &lt;
          </Button>
          <p>{currentDate}</p>
          <Button disabled={!hasNext()} variant='outline' onClick={next}>
            &gt;
          </Button>
        </div>
      )}
      {data && (
        <div className='grid w-full gap-1.5'>
          <div className='flex gap-2 items-center'>
            <div className='flex-1'>{<p className=''>选择一项结果生成文档</p>}</div>
          </div>
          <div className='w-full gap-1.5'>
            <div className=''>
              <List insights={data} selected={selectedInsight} onOpen={(id) => selectInsight(id)} onDelete={unlink} onReport={report} onMore={getMore} isGettingMore={mutMore.isPending} error={mut.error} />
            </div>
            <p className='text-sm text-muted-foreground mt-4'>共{Object.keys(data).length}条结果</p>
          </div>
        </div>
      )}
      <div className='my-6 flex flex-col gap-4 w-36 text-left'>
        <Button variant='outline' onClick={() => navigate("/articles")}>
          查看所有文章
        </Button>
        <a href={`${import.meta.env.VITE_PB_BASE}/_/`} target='__blank' className='text-sm underline'>
          数据库管理 &gt;
        </a>
      </div>
    </>
  )
}

export default InsightsScreen
