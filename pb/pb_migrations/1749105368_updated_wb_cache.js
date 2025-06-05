/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_3849151725")

  // remove field
  collection.fields.removeById("date1542800728")

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3849151725")

  // add field
  collection.fields.addAt(13, new Field({
    "hidden": false,
    "id": "date1542800728",
    "max": "",
    "min": "",
    "name": "field",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "date"
  }))

  return app.save(collection)
})
