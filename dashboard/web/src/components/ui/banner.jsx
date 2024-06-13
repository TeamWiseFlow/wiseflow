import * as React from "react"
import { cn } from "@/lib/utils"

const Banner = React.forwardRef(({ className, ...props }, ref) => (
  <div className={cn("max-h-24 overflow-y-scroll fixed top-0 right-8 min-w-[200px] max-w-[500px] ml-0 mr-0 bg-red-100 text-red-900 px-6 py-2 border border-red-400 rounded-sm shadow-sm text-sm disabled:cursor-not-allowed", className)} ref={ref} {...props} />
))
Banner.displayName = "Banner"

export { Banner }
