/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_1970519189")

  // add field
  collection.fields.addAt(3, new Field({
    "cascadeDelete": false,
    "collectionId": "pbc_3385864241",
    "hidden": false,
    "id": "relation2655548471",
    "maxSelect": 999,
    "minSelect": 0,
    "name": "focus_points",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "relation"
  }))

  // add field
  collection.fields.addAt(4, new Field({
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

  // add field
  collection.fields.addAt(5, new Field({
    "autogeneratePattern": "",
    "hidden": false,
    "id": "text2870082381",
    "max": 0,
    "min": 0,
    "name": "search_engine_keywords",
    "pattern": "",
    "presentable": false,
    "primaryKey": false,
    "required": false,
    "system": false,
    "type": "text"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_1970519189")

  // remove field
  collection.fields.removeById("relation2655548471")

  // remove field
  collection.fields.removeById("relation3154160227")

  // remove field
  collection.fields.removeById("text2870082381")

  return app.save(collection)
})
