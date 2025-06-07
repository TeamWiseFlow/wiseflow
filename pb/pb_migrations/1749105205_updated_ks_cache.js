/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_265345011")

  // remove field
  collection.fields.removeById("autodate3332085495")

  // add field
  collection.fields.addAt(12, new Field({
    "hidden": false,
    "id": "date3332085495",
    "max": "",
    "min": "",
    "name": "updated",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "date"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_265345011")

  // add field
  collection.fields.addAt(12, new Field({
    "hidden": false,
    "id": "autodate3332085495",
    "name": "updated",
    "onCreate": true,
    "onUpdate": false,
    "presentable": false,
    "system": false,
    "type": "autodate"
  }))

  // remove field
  collection.fields.removeById("date3332085495")

  return app.save(collection)
})
