/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("lft7642skuqmry7")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "pwy2iz0b",
    "name": "source",
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
  const collection = dao.findCollectionByNameOrId("lft7642skuqmry7")

  // remove
  collection.schema.removeField("pwy2iz0b")

  return dao.saveCollection(collection)
})
