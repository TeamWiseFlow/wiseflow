/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_2001081480")

  // remove field
  collection.fields.removeById("number1152796692")

  // remove field
  collection.fields.removeById("bool806155165")

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_2001081480")

  // add field
  collection.fields.addAt(2, new Field({
    "hidden": false,
    "id": "number1152796692",
    "max": null,
    "min": null,
    "name": "per_hours",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

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
