/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = new Collection({
    "createRule": null,
    "deleteRule": null,
    "fields": [
      {
        "autogeneratePattern": "[a-z0-9]{15}",
        "hidden": false,
        "id": "text3208210256",
        "max": 15,
        "min": 15,
        "name": "id",
        "pattern": "^[a-z0-9]+$",
        "presentable": false,
        "primaryKey": true,
        "required": true,
        "system": true,
        "type": "text"
      },
      {
        "hidden": false,
        "id": "select1542800728",
        "maxSelect": 1,
        "name": "field",
        "presentable": true,
        "required": false,
        "system": false,
        "type": "select",
        "values": [
          "web",
          "rss",
          "ks",
          "wb",
          "mp"
        ]
      },
      {
        "autogeneratePattern": "",
        "hidden": false,
        "id": "text3473537283",
        "max": 0,
        "min": 0,
        "name": "creators",
        "pattern": "",
        "presentable": false,
        "primaryKey": false,
        "required": false,
        "system": false,
        "type": "text"
      },
      {
        "exceptDomains": null,
        "hidden": false,
        "id": "url4101391790",
        "name": "url",
        "onlyDomains": null,
        "presentable": false,
        "required": false,
        "system": false,
        "type": "url"
      }
    ],
    "id": "pbc_1124997656",
    "indexes": [],
    "listRule": null,
    "name": "sources",
    "system": false,
    "type": "base",
    "updateRule": null,
    "viewRule": null
  });

  return app.save(collection);
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_1124997656");

  return app.delete(collection);
})
