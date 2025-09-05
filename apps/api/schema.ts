import { gql } from 'apollo-server';

export default gql`
  enum NodeType { DEITY, TEXT, CONCEPT, CHARACTER, PLACE, EVENT, SYMBOL }
  enum RelType  { AVATAR_OF, CHILD_OF, CONSORT_OF, SIBLING_OF, APPEARS_IN, CONTAINED_IN,
                  SYMBOLIZES, WIELDS, RESIDES_IN, FOUGHT_AGAINST, ASSOCIATED_WITH, MEMBER_OF,
                  MENTOR_OF, DEVOTEE_OF }

  type Media { kind: String!, uri: String!, caption: String, license: String, author: String, sourceUrl: String }
  type SourceRef { kind: String!, url: String!, oldid: Int!, license: String!, modified: Boolean! }

  type Node {
    id: ID!, slug: String!, qid: String, type: NodeType!, title: String!,
    short: String!, long: String, aliases: [String!]!, tags: [String!]!, media: [Media!]!,
    sources: [SourceRef!]!
    edges(radius: Int = 1): [Edge!]!
  }

  type Edge { from: ID!, to: ID!, rel: RelType!, weight: Float, note: String, source: String, variant: String }
  type Query {
    node(slug: String!): Node
    search(q: String!, type: NodeType, page: Int = 1, limit: Int = 20): [Node!]!
    subgraph(center: String!, radius: Int = 1): [Edge!]!
    timeline(yuga: String): [Event!]!
    path(slug: String!): Path
  }
`;
