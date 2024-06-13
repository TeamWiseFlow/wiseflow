/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const collection = new Collection({
    "id": "bc3g5s66bcq1qjp",
    "created": "2024-04-07 00:31:40.644Z",
    "updated": "2024-04-07 00:31:40.644Z",
    "name": "article_translation",
    "type": "base",
    "system": false,
    "schema": [
      {
        "system": false,
        "id": "t2jqr7cs",
        "name": "title",
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
        "id": "dr9kt3dn",
        "name": "abstract",
        "type": "text",
        "required": false,
        "presentable": false,
        "unique": false,
        "options": {
          "min": null,
          "max": null,
          "pattern": ""
        }
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
  const collection = dao.findCollectionByNameOrId("bc3g5s66bcq1qjp");

  return dao.deleteCollection(collection);
})
