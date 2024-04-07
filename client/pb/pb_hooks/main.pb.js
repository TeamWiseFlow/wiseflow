routerAdd(
  "POST",
  "/save",
  (c) => {
    const data = $apis.requestInfo(c).data
    // console.log(data)

    let dir = $os.getenv("PROJECT_DIR")
    if (dir) {
      dir = dir + "/"
    }
    // console.log(dir)

    const collection = $app.dao().findCollectionByNameOrId("documents")
    const record = new Record(collection)
    const form = new RecordUpsertForm($app, record)

    // or form.loadRequest(request, "")
    form.loadData({
      workflow: data.workflow,
      insight: data.insight,
      task: data.task,
    })

    // console.log(dir + data.file)
    const f1 = $filesystem.fileFromPath(dir + data.file)
    form.addFiles("files", f1)

    form.submit()

    return c.json(200, record)
  },
  $apis.requireRecordAuth()
)

routerAdd(
  "GET",
  "/insight_dates",
  (c) => {
    let result = arrayOf(
      new DynamicModel({
        created: "",
      })
    )

    $app.dao().db().newQuery("SELECT DISTINCT DATE(created) as created FROM insights").all(result)

    return c.json(
      200,
      result.map((r) => r.created)
    )
  },
  $apis.requireAdminAuth()
)

routerAdd(
  "GET",
  "/article_dates",
  (c) => {
    let result = arrayOf(
      new DynamicModel({
        created: "",
      })
    )

    $app.dao().db().newQuery("SELECT DISTINCT DATE(created) as created FROM articles").all(result)

    return c.json(
      200,
      result.map((r) => r.created)
    )
  },
  $apis.requireAdminAuth()
)
