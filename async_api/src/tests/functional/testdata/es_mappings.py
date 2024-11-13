es_movie_mappings = {
  "dynamic": "strict",
  "properties": {
    "id": {
      "type": "keyword"
    },
    "imdb_rating": {
      "type": "float"
    },
    "genre": {
      "type": "keyword"
    },
    "title": {
      "type": "text",
      "analyzer": "ru_en",
      "fields": {
        "raw": {
          "type":  "keyword"
        }
      }
    },
    "description": {
      "type": "text",
      "analyzer": "ru_en"
    },
    "directors_names": {
      "type": "text",
      "analyzer": "ru_en"
    },
    "actors_names": {
      "type": "text",
      "analyzer": "ru_en"
    },
    "writers_names": {
      "type": "text",
      "analyzer": "ru_en"
    },
    "actors": {
      "type": "nested",
      "dynamic": "strict",
      "properties": {
        "id": {
          "type": "keyword"
        },
        "name": {
          "type": "text",
          "analyzer": "ru_en"
        }
      }
    },
    "directors": {
      "type": "nested",
      "dynamic": "strict",
      "properties": {
        "id": {
          "type": "keyword"
        },
        "name": {
          "type": "text",
          "analyzer": "ru_en"
        }
      }
    },
    "writers": {
      "type": "nested",
      "dynamic": "strict",
      "properties": {
        "id": {
          "type": "keyword"
        },
        "name": {
          "type": "text",
          "analyzer": "ru_en"
        }
      }
    }
  }
}

es_person_mappings = {
  "dynamic": "strict",
  "properties": {
    "id": {
      "type": "keyword"
    },
    "full_name": {
      "type": "text",
      "analyzer": "ru_en",
      "fields": {
        "raw": {
          "type":  "keyword"
        }
      }
    },
    "created": {
      "type": "date"
    },
    "modified": {
      "type": "date"
    }
  }
}

es_genre_mappings = {
  "dynamic": "strict",
  "properties": {
    "id": {
        "type": "keyword"
    },
    "name": {
      "type": "text",
      "analyzer": "ru_en",
      "fields": {
        "raw": {
          "type":  "keyword"
        }
      }
    },
    "description": {
      "type": "text",
      "analyzer": "ru_en",
      "fields": {
        "raw": {
          "type":  "keyword"
        }
      }
    },
    "created": {
      "type": "date"
    },
    "modified": {
      "type": "date"
    }
  }
}
