import { QueryClient, QueryClientProvider, QueryCache, useQueryClient } from "@tanstack/react-query"
import { ReactQueryDevtools } from "@tanstack/react-query-devtools"

import "./App.css"

import { Toaster } from "@/components/ui/toaster"
import { useToast } from "@/components/ui/use-toast"
import { Button } from "@/components/ui/button"
import LoginScreen from "@/components/screen/login"
// import Steps from "@/components/screen/steps"
import InsightsScreen from "@/components/screen/insights"
import ArticlesScreen from "@/components/screen/articles"
import ReportScreen from "@/components/screen/report"

import { isAuth } from "@/store"

const queryClient = new QueryClient()

import { Route, Switch, useLocation } from "wouter"

function App() {
  const [, setLocation] = useLocation()
  if (!isAuth()) {
    setLocation("/login")
  }
  // const { toast } = useToast()

  return (
    <QueryClientProvider client={queryClient}>
      <Switch>
        <Route path='/' component={InsightsScreen} />
        <Route path='/login' component={LoginScreen} />
        <Route path='/insights' component={InsightsScreen} />
        <Route path='/articles' component={ArticlesScreen} />
        <Route path='/report/:insight_id' component={ReportScreen} />
        <Route>404</Route>
      </Switch>
      {/* <Button
        onClick={() => {
          toast({
            title: "Scheduled: Catch up",
            description: "Friday, February 10, 2023 at 5:57 PM",
          })
        }}
      >
        Show Toast
      </Button> */}
      <Toaster />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

export default App
