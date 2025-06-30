/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_3385864241")

  // remove field
  collection.fields.removeById("bool3035683751")

  // add field
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
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3385864241")

  // add field
  collection.fields.addAt(5, new Field({
    "hidden": false,
    "id": "bool3035683751",
    "name": "search",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "bool"
  }))

  // remove field
  collection.fields.removeById("select3035683751")

  return app.save(collection)
})
