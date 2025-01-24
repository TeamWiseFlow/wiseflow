/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_3385864241")

  // add field
  collection.fields.addAt(6, new Field({
    "hidden": false,
    "id": "bool826963346",
    "name": "search_engine",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "bool"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3385864241")

  // remove field
  collection.fields.removeById("bool826963346")

  return app.save(collection)
})
