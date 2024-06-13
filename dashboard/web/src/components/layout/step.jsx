import { Button } from "@/components/ui/button"

export default function StepLayout({ title, description, children, navigate }) {
  return (
    <>
      <div className='mx-auto text-left'>
        <div className='flex gap-4'>
          <div className='flex-1'>
            <h1 className='mt-10 scroll-m-20 pb-2 text-3xl font-semibold tracking-tight transition-colors first:mt-0'>{title}</h1>
            {description && <p className='text-xl text-muted-foreground'>{description}</p>}
          </div>
          {/* <Button variant='outline' onClick={() => navigate("/start")}>
            新建任务
          </Button> */}
        </div>
        <hr className='my-4'></hr>
        {children}
      </div>
    </>
  )
}
