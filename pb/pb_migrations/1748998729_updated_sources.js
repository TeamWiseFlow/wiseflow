/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_1124997656")

  // update field
  collection.fields.addAt(1, new Field({
    "hidden": false,
    "id": "select1542800728",
    "maxSelect": 1,
    "name": "type",
    "presentable": true,
    "required": false,
    "system": false,
    "type": "select",
    "values": [
      "web",
      "rss",
      "ks",
      "wb",
      "mp"
    ]
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_1124997656")

  // update field
  collection.fields.addAt(1, new Field({
    "hidden": false,
    "id": "select1542800728",
    "maxSelect": 1,
    "name": "field",
    "presentable": true,
    "required": false,
    "system": false,
    "type": "select",
    "values": [
      "web",
      "rss",
      "ks",
      "wb",
      "mp"
    ]
  }))

  return app.save(collection)
})
