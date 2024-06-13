/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("bc3g5s66bcq1qjp")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "lbxw5pra",
    "name": "tag",
    "type": "relation",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {
      "collectionId": "nvf6k0yoiclmytu",
      "cascadeDelete": false,
      "minSelect": null,
      "maxSelect": null,
      "displayFields": null
    }
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("bc3g5s66bcq1qjp")

  // remove
  collection.schema.removeField("lbxw5pra")

  return dao.saveCollection(collection)
})
