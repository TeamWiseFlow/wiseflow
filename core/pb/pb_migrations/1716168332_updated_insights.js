/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("h3c6pqhnrfo4oyf")

  // update
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "j65p3jji",
    "name": "tag",
    "type": "relation",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {
      "collectionId": "nvf6k0yoiclmytu",
      "cascadeDelete": false,
      "minSelect": null,
      "maxSelect": 1,
      "displayFields": null
    }
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("h3c6pqhnrfo4oyf")

  // update
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "j65p3jji",
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
})
