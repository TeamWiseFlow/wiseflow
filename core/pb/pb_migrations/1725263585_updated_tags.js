/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("nvf6k0yoiclmytu")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "vkgtujiz",
    "name": "explaination",
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
  const collection = dao.findCollectionByNameOrId("nvf6k0yoiclmytu")

  // remove
  collection.schema.removeField("vkgtujiz")

  return dao.saveCollection(collection)
})
