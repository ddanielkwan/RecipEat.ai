package main.java.com.recipeat_search.recipeat_search.index;

import org.opensearch.client.RestHighLevelClient;
import org.opensearch.client.RestClient;
import org.opensearch.client.RestClientBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.beans.factory.annotation.Value;

@Configuration
public class IndexConfiguration {

    @Value("${opensearch.url}")
    private String openSearchUrl;

    @Bean
    public RestHighLevelClient client() {
        RestClientBuilder builder = RestClient.builder(new HttpHost(openSearchUrl, 9200, "https"));
        return new RestHighLevelClient(builder);
    }

}
