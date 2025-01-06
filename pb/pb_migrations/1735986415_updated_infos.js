/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_629947526")

  // add field
  collection.fields.addAt(7, new Field({
    "hidden": false,
    "id": "json2669555100",
    "maxSize": 0,
    "name": "references",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "json"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_629947526")

  // remove field
  collection.fields.removeById("json2669555100")

  return app.save(collection)
})
