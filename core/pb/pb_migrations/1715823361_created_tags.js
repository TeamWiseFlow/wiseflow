/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const collection = new Collection({
    "id": "nvf6k0yoiclmytu",
    "created": "2024-05-16 01:36:01.108Z",
    "updated": "2024-05-16 01:36:01.108Z",
    "name": "tags",
    "type": "base",
    "system": false,
    "schema": [
      {
        "system": false,
        "id": "0th8uax4",
        "name": "name",
        "type": "text",
        "required": false,
        "presentable": false,
        "unique": false,
        "options": {
          "min": null,
          "max": null,
          "pattern": ""
        }
      },
      {
        "system": false,
        "id": "l6mm7m90",
        "name": "activated",
        "type": "bool",
        "required": false,
        "presentable": false,
        "unique": false,
        "options": {}
      }
    ],
    "indexes": [],
    "listRule": null,
    "viewRule": null,
    "createRule": null,
    "updateRule": null,
    "deleteRule": null,
    "options": {}
  });

  return Dao(db).saveCollection(collection);
}, (db) => {
  const dao = new Dao(db);
  const collection = dao.findCollectionByNameOrId("nvf6k0yoiclmytu");

  return dao.deleteCollection(collection);
})
