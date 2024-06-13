// import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
// import * as z from 'zod'
import { useMutation } from '@tanstack/react-query'

import { Button } from '@/components/ui/button'
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'

import { useLocation } from 'wouter'
import { login } from '@/store'

// const FormSchema = z.object({
//   username: z.string().nonempty('请填写用户名'),
//   password: z.string().nonempty('请填写密码'),
// })

export function AdminLoginScreen() {
  const form = useForm({
    // resolver: zodResolver(FormSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  })

  const [, setLocation] = useLocation()
  const mutation = useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      setLocation('/')
    },
  })

  function onSubmit(e) {
    mutation.mutate({ username: form.getValues('username'), password: form.getValues('password') })
  }

  return (
    <div className="max-w-sm mx-auto text-left">
      <h2 className="mt-10 scroll-m-20 pb-2 text-3xl font-semibold tracking-tight transition-colors first:mt-0">登录</h2>
      <p className="text-xl text-muted-foreground">输入账号及密码</p>
      <hr className="my-6"></hr>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="mx-auto space-y-6">
          <FormField
            control={form.control}
            name="username"
            render={({ field }) => (
              <FormItem className="text-left">
                <FormLabel>用户名</FormLabel>
                <FormControl>
                  <Input placeholder="" {...field} />
                </FormControl>
                <FormDescription></FormDescription>
                <FormMessage>{mutation?.error?.response?.data?.['identity']?.message}</FormMessage>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem className="text-left">
                <FormLabel>密码</FormLabel>
                <FormControl>
                  <Input placeholder="" {...field} type="password" />
                </FormControl>
                <FormDescription></FormDescription>
                <FormMessage>{mutation?.error?.response?.data?.['password']?.message}</FormMessage>
              </FormItem>
            )}
          />
          <p className="text-sm text-destructive">{mutation?.error?.message}</p>
          <Button type="submit">登录</Button>
        </form>
      </Form>
    </div>
  )
}

export default AdminLoginScreen
