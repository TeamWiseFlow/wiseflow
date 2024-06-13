/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("lft7642skuqmry7")

  collection.listRule = "@request.auth.id != \"\" && @request.auth.tag:each ?~ tag:each"
  collection.viewRule = "@request.auth.id != \"\" && @request.auth.tag:each ?~ tag:each"

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("lft7642skuqmry7")

  collection.listRule = null
  collection.viewRule = null

  return dao.saveCollection(collection)
})
