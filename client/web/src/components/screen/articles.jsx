import { useEffect } from "react"
import { Button } from "@/components/ui/button"
import { ArticleList } from "../article-list"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Languages } from "lucide-react"
import { ButtonLoading } from "@/components/ui/button-loading"
import { useDatePager, useArticleDates, useArticles, translations } from "@/store"

import { useLocation } from "wouter"

function ArticlesScreen({}) {
  const [, navigate] = useLocation()

  const queryDates = useArticleDates()
  const { index, last, next, hasLast, hasNext } = useDatePager(queryDates.data)
  const currentDate = queryDates.data && index >= 0 ? queryDates.data[index] : ""
  const query = useArticles(currentDate)
  const queryClient = useQueryClient()

  const mut = useMutation({
    mutationFn: (data) => {
      return translations(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["articles", currentDate] })
    },
  })

  function trans() {
    mut.mutate({ article_ids: query.data.filter((d) => !d.translation_result).map((d) => d.id) })
  }

  return (
    <>
      <h2>文章</h2>
      {query.isError && <p className='text-red-500 my-4'>{query.error.message}</p>}
      <div className='my-6 flex gap-4 w-fit'>
        <Button onClick={() => navigate("/insights")}>查看分析结果</Button>
        {mut.isPending && <ButtonLoading />}
        {!mut.isPending && query.data && query.data.length > 0 && query.data.filter((a) => !a.translation_result).length > 0 && (
          <Button variant='outline' className='text-blue-400 mb-6' onClick={trans}>
            <Languages className='w-4 h-4' />
            一键翻译
          </Button>
        )}
      </div>
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
      {/* {completed && !Object.values(query.data.articles)[0]["zh-cn"] && (
        <Button variant='link' className='text-blue-400 mb-6' onClick={trans}>
          <Languages className='w-4 h-4' />
          一键翻译
        </Button>
      )} */}

      {query.data && <ArticleList data={query.data} />}

      <div className='my-6 flex gap-4'>
        <Button onClick={() => navigate("/insights")}>查看分析结果</Button>
      </div>
    </>
  )
}

export default ArticlesScreen
