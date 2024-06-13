import { Button } from "@/components/ui/button"
import { Delete } from "lucide-react"

// data expecting object {"0":{}, "1":{}}
export function ArticleList({ data, showActions, onDelete }) {
  return (
    <div className='grid w-full gap-1.5'>
      <div className='border overflow-hidden'>
        {data &&
          data.map((article, i) => (
            <div key={i} className='border-b px-4 py-2 flex gap-2'>
              <div className='flex-1 whitespace-nowrap min-w-0'>
                <p className='font-normal w-full truncate underline text-left'>
                  <a href={article.url} target='_blank' rel='noreferrer'>
                    {article.expand?.translation_result?.title || article.title}
                  </a>
                </p>
                <p className='font-light min-w-0 truncate text-left'>{article.expand?.translation_result?.abstract || article.abstract}</p>
              </div>
              <div>
                {showActions && (
                  <Button variant='ghost' className='text-red-500' onClick={() => onDelete(article.id)}>
                    <Delete className='h-4 w-4' />
                  </Button>
                )}
              </div>
            </div>
          ))}
      </div>
      {data && <p className='text-sm text-muted-foreground mt-4'>共{Object.keys(data).length}篇文章</p>}
    </div>
  )
}
