/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("lft7642skuqmry7")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "famdh2fv",
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
  const collection = dao.findCollectionByNameOrId("lft7642skuqmry7")

  // remove
  collection.schema.removeField("famdh2fv")

  return dao.saveCollection(collection)
})
