package com.recipeat_search.recipeat_search;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class RecipeatSearchApplication {

	public static void main(String[] args) {
		SpringApplication.run(RecipeatSearchApplication.class, args);
	}

}

@Component
class OpenSearchIndexInitializer {

	@Autowired
	private RestHighLevelClient client;

	@EventListener(ApplicationReadyEvent.class)
	public void createIndex() {
		try {
			CreateIndexRequest request = new CreateIndexRequest("recipes");
			request.settings(Settings.builder()
					.put("index.number_of_shards", 3)
					.put("index.number_of_replicas", 2));

			String mapping = """
					    {
					        "properties": {
					            "name": { "type": "text" },
					            "description": { "type": "text" },
					            "ingredients": { "type": "text" },
					            "instructions": { "type": "text" }
					        }
					    }
					""";

			request.mapping(mapping, XContentType.JSON);

			CreateIndexResponse createIndexResponse = client.indices().create(request, RequestOptions.DEFAULT);
			if (createIndexResponse.isAcknowledged()) {
				System.out.println("Index created successfully.");
			} else {
				System.out.println("Index creation failed.");
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

	}
}
