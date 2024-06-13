/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("h3c6pqhnrfo4oyf")

  collection.listRule = "@request.auth.id != \"\" && @request.auth.tag:each ?~ tag:each"

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("h3c6pqhnrfo4oyf")

  collection.listRule = null

  return dao.saveCollection(collection)
})
