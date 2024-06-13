/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("bc3g5s66bcq1qjp")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "tmwf6icx",
    "name": "raw",
    "type": "relation",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {
      "collectionId": "lft7642skuqmry7",
      "cascadeDelete": false,
      "minSelect": null,
      "maxSelect": 1,
      "displayFields": null
    }
  }))

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "hsckiykq",
    "name": "content",
    "type": "text",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {
      "min": null,
      "max": null,
      "pattern": ""
    }
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("bc3g5s66bcq1qjp")

  // remove
  collection.schema.removeField("tmwf6icx")

  // remove
  collection.schema.removeField("hsckiykq")

  return dao.saveCollection(collection)
})
