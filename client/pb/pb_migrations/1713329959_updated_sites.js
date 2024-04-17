/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("sma08jpi5rkoxnh")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "8x8n2a47",
    "name": "activated",
    "type": "bool",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {}
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("sma08jpi5rkoxnh")

  // remove
  collection.schema.removeField("8x8n2a47")

  return dao.saveCollection(collection)
})
