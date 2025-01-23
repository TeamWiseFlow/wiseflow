/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
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

  // add field
  collection.fields.addAt(4, new Field({
    "hidden": false,
    "id": "number3171882809",
    "max": null,
    "min": null,
    "name": "per_hour",
    "onlyInt": false,
    "presentable": false,
    "required": true,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(5, new Field({
    "cascadeDelete": false,
    "collectionId": "pbc_2001081480",
    "hidden": false,
    "id": "relation3154160227",
    "maxSelect": 999,
    "minSelect": 0,
    "name": "sites",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "relation"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3385864241")

  // remove field
  collection.fields.removeById("bool806155165")

  // remove field
  collection.fields.removeById("number3171882809")

  // remove field
  collection.fields.removeById("relation3154160227")

  return app.save(collection)
})
