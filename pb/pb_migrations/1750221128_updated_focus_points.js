/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_3385864241")

  // add field
  collection.fields.addAt(10, new Field({
    "hidden": false,
    "id": "bool547014461",
    "name": "peoplefind",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "bool"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3385864241")

  // remove field
  collection.fields.removeById("bool547014461")

  return app.save(collection)
})
