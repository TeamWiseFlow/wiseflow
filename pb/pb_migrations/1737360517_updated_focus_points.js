/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_3385864241")

  // remove field
  collection.fields.removeById("bool806155165")

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3385864241")

  // add field
  collection.fields.addAt(3, new Field({
    "hidden": false,
    "id": "bool806155165",
    "name": "activated",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "bool"
  }))

  return app.save(collection)
})
