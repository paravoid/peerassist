import urllib3
import gql
from gql.transport.requests import RequestsHTTPTransport


BATCH_SIZE = 150_000  # currently fits everything in one batch
QUERY = gql.gql(
    """
        query fetch_asns($first: Int, $offset: Int) {
          asns(first: $first, offset: $offset) {
            totalCount
            pageInfo {
              first
              hasNextPage
            }
            edges {
              node {
                asn
                rank
              }
            }
          }
        }
    """
)


def fetch_from_caida():
    # we don't really care about traffic security here
    urllib3.disable_warnings()

    caida_transport = RequestsHTTPTransport(
        url="https://api.asrank.caida.org/v2/graphql",
        headers={"Content-type": "application/json"},
        use_json=True,
        verify=False,
    )

    client = gql.Client(retries=3, transport=caida_transport)

    offset = 0
    has_next_page = True
    while has_next_page:
        response = client.execute(QUERY, {"first": BATCH_SIZE, "offset": offset})
        has_next_page = response["asns"]["pageInfo"]["hasNextPage"]
        total_count = response["asns"]["totalCount"]
        offset += BATCH_SIZE

        for edge in response["asns"]["edges"]:
            node = edge["node"]
            asn, rank = node["asn"], node["rank"]
            yield int(asn), rank
