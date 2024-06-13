/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("h3c6pqhnrfo4oyf")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "d13734ez",
    "name": "tag",
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
  const collection = dao.findCollectionByNameOrId("h3c6pqhnrfo4oyf")

  // remove
  collection.schema.removeField("d13734ez")

  return dao.saveCollection(collection)
})
