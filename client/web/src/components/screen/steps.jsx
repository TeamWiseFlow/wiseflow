import { useState, useTransition } from "react"
import { Banner } from "@/components/ui/banner"
import StepLayout from "@/components/layout/step"
import StartScreen from "@/components/screen/start"
import ArticlesScreen from "@/components/screen/articles"
import InsightsScreen from "@/components/screen/insights"
import ReportScreen from "@/components/screen/report"

import { Loader2 } from "lucide-react"
import { useEffect } from "react"
import { useClientStore, useData } from "@/store"

const TITLE = "情报分析"

function Steps() {
  let [currentScreen, setCurrentScreen] = useState("/insights")
  const [isPending, startTransition] = useTransition()
  const selectInsight = useClientStore((state) => state.selectInsight)
  const selectedInsight = useClientStore((state) => state.selectedInsight)
  const taskId = useClientStore((state) => state.taskId)
  const setTaskId = useClientStore((state) => state.setTaskId)

  // useEffect(() => {
  //   const searchParams = new URLSearchParams(document.location.search)
  //   let taskIdSpecified = searchParams.get("task_id")
  //   if (taskIdSpecified) {
  //     setTaskId(taskIdSpecified)
  //   }
  // }, [])

  // const query = useData(taskId)
  // console.log(taskId, query.data)

  // useEffect(() => {
  //   // navigate away from /start
  //   if (query.data && currentScreen == "/start") {
  //     let state = query.data
  //     if (state.articles && Object.keys(state.articles).length > 0) {
  //       setCurrentScreen("/articles")
  //     }

  //     if (state.insights && Object.keys(state.insights).length > 0) {
  //       if (selectedInsight && state.insights[selectedInsight]?.report?.file) {
  //         setCurrentScreen("/report")
  //       } else {
  //         setCurrentScreen("/insights")
  //       }
  //     } else {
  //       selectInsight(null) // deselect
  //     }
  //   }
  // }, [query.data])

  // const errors = (query.isError && [query.error]) || (query.data && query.data.errors && query.data.errors.length > 0 && query.data.errors)

  function navigate(screen) {
    startTransition(() => {
      setCurrentScreen(screen)
    })
  }

  // console.log("screen:", currenScreen)

  let content, title
  if (currentScreen == "/start") {
    title = TITLE + " > " + "数据来源"
    content = <StartScreen navigate={navigate} />
  } else if (currentScreen == "/articles") {
    title = TITLE + " > " + "文章列表"
    content = <ArticlesScreen navigate={navigate} />
  } else if (currentScreen == "/insights") {
    title = TITLE + " > " + "分析结果"
    content = <InsightsScreen navigate={navigate} />
  } else if (currentScreen == "/report") {
    title = TITLE + " > " + "生成报告"
    content = <ReportScreen navigate={navigate} />
  }

  return (
    <StepLayout title={title} isPending={isPending} navigate={navigate}>
      {content}
      {/* {errors && (
        <Banner>
          {errors.map((e, i) => (
            <p key={i}>{e}</p>
          ))}
        </Banner>
      )} */}

      {/* {query.data && query.data.working && (
        <div className='fixed bottom-2 right-2 text-sm'>
          <Loader2 className='w-4 h-4 animate-spin text-red-500'></Loader2>
        </div>
      )} */}
      {/* {query.isFetching && (
        <div className='fixed bottom-2 right-2 text-sm'>
          <Loader2 className='w-4 h-4 animate-spin'></Loader2>
        </div>
      )} */}
      {/* <div className='left-8 bottom-8 text-sm text-muted-foreground mt-8'>task_id:{taskId}</div> */}
    </StepLayout>
  )
}

export default Steps
