/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_3385864241")

  // update field
  collection.fields.addAt(10, new Field({
    "hidden": false,
    "id": "select3035683751",
    "maxSelect": 6,
    "name": "search",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "select",
    "values": [
      "bing",
      "wb",
      "ks",
      "github",
      "ebay",
      "arxiv"
    ]
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3385864241")

  // update field
  collection.fields.addAt(10, new Field({
    "hidden": false,
    "id": "select3035683751",
    "maxSelect": 2,
    "name": "search",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "select",
    "values": [
      "bing",
      "wb",
      "ks",
      "github",
      "ebay",
      "arxiv"
    ]
  }))

  return app.save(collection)
})
