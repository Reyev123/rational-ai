"""Add architecture diagrams to the ShopAI project."""
import yaml, os

os.chdir(r"c:\Users\Reyev\Documents\_hackathon\rational-ai")

p = yaml.safe_load(open(".rai/project.yaml", encoding="utf-8"))

diagrams = [
    {
        "id": "DIA-001",
        "title": "System Architecture - Microservices Overview",
        "type": "component",
        "description": "High-level component diagram showing all ShopAI microservices and their interactions",
        "mermaid_code": """graph TB
    subgraph CLIENT["Client Layer"]
        PWA["Frontend PWA\\nReact + Next.js"]
        MOBILE["Mobile Browser\\nPWA + Push"]
    end

    subgraph GATEWAY["API Gateway Layer"]
        GW["API Gateway\\nKong / NGINX\\nRate Limiting + Auth"]
    end

    subgraph SERVICES["Microservices Layer"]
        AUTH["Auth Service\\nFastAPI + Redis\\nJWT + OAuth2"]
        CATALOG["Product Catalog\\nFastAPI + PostgreSQL\\n+ Elasticsearch"]
        INVENTORY["Inventory Service\\nFastAPI + PostgreSQL\\nWebSocket Updates"]
        ORDERS["Order & Payment\\nFastAPI + Stripe SDK"]
        RECO["Recommendation Engine\\nTensorFlow Serving\\n+ Redis Cache"]
    end

    subgraph MESSAGING["Event Layer"]
        KAFKA["Event Bus\\nApache Kafka"]
    end

    subgraph DATA["Data Layer"]
        PG[("PostgreSQL\\nPrimary DB")]
        REDIS[("Redis\\nCache + Sessions")]
        ES[("Elasticsearch\\nProduct Search")]
    end

    PWA --> GW
    MOBILE --> GW
    GW --> AUTH
    GW --> CATALOG
    GW --> INVENTORY
    GW --> ORDERS
    GW --> RECO

    AUTH --> REDIS
    CATALOG --> PG
    CATALOG --> ES
    INVENTORY --> PG
    INVENTORY --> KAFKA
    ORDERS --> PG
    ORDERS --> KAFKA
    RECO --> REDIS
    RECO --> CATALOG

    KAFKA --> INVENTORY
    KAFKA --> ORDERS
    KAFKA --> RECO

    style CLIENT fill:#E8F4FD,stroke:#7FB3D3,stroke-width:2px
    style GATEWAY fill:#FFF8E7,stroke:#E6C97A,stroke-width:2px
    style SERVICES fill:#F0FFF0,stroke:#90C695,stroke-width:2px
    style MESSAGING fill:#F5F0FF,stroke:#B0A0D4,stroke-width:2px
    style DATA fill:#FFFAF0,stroke:#D4B896,stroke-width:2px""",
    },
    {
        "id": "DIA-002",
        "title": "Service Communication - Purchase Flow",
        "type": "sequence",
        "description": "Customer purchase flow showing inter-service communication",
        "mermaid_code": """sequenceDiagram
    participant C as Customer
    participant GW as API Gateway
    participant AUTH as Auth Service
    participant CAT as Product Catalog
    participant RECO as Recommendation
    participant INV as Inventory
    participant ORD as Order Service
    participant PAY as Stripe
    participant K as Kafka

    C->>GW: Browse products
    GW->>AUTH: Validate JWT
    AUTH-->>GW: Token valid
    GW->>CAT: GET /products
    CAT-->>GW: Product list
    GW->>RECO: GET /recommendations
    RECO-->>GW: Personalized picks
    GW-->>C: Products + Recommendations

    C->>GW: POST /orders (checkout)
    GW->>INV: Check stock
    INV-->>GW: Stock confirmed
    GW->>ORD: Create order
    ORD->>PAY: Charge payment
    PAY-->>ORD: Payment success
    ORD->>K: OrderCreated event
    K->>INV: Update stock
    K->>RECO: Update user history
    ORD-->>GW: Order confirmed
    GW-->>C: Order confirmed""",
    },
    {
        "id": "DIA-003",
        "title": "Deployment Architecture - AWS EKS",
        "type": "deployment",
        "description": "AWS + Kubernetes deployment topology for production environment",
        "mermaid_code": """graph TB
    subgraph AWS["AWS Cloud"]
        subgraph EKS["EKS Kubernetes Cluster"]
            subgraph NS_APP["namespace: shopai"]
                GW_POD["API Gateway\\n3 replicas"]
                AUTH_POD["Auth Service\\n2 replicas"]
                CAT_POD["Catalog Service\\n3 replicas"]
                INV_POD["Inventory Service\\n2 replicas"]
                ORD_POD["Order Service\\n3 replicas"]
                RECO_POD["Recommendation\\n2 replicas + GPU"]
            end
            subgraph NS_DATA["namespace: data"]
                KAFKA_POD["Kafka Cluster\\n3 brokers"]
                REDIS_POD["Redis Cluster\\n3 nodes"]
            end
        end

        subgraph MANAGED["Managed Services"]
            RDS[("RDS PostgreSQL\\nMulti-AZ")]
            ESVC[("OpenSearch\\n3 nodes")]
            S3[("S3\\nStatic Assets")]
            CF["CloudFront CDN"]
        end

        ALB["Application\\nLoad Balancer"]
    end

    USERS["Users"] --> CF
    CF --> ALB
    ALB --> GW_POD
    GW_POD --> AUTH_POD
    GW_POD --> CAT_POD
    GW_POD --> INV_POD
    GW_POD --> ORD_POD
    GW_POD --> RECO_POD
    CAT_POD --> RDS
    INV_POD --> RDS
    ORD_POD --> RDS
    CAT_POD --> ESVC
    AUTH_POD --> REDIS_POD
    RECO_POD --> REDIS_POD
    INV_POD --> KAFKA_POD
    ORD_POD --> KAFKA_POD
    CF --> S3

    style AWS fill:#FFF8E7,stroke:#E6C97A,stroke-width:2px
    style EKS fill:#E8F4FD,stroke:#7FB3D3,stroke-width:2px
    style NS_APP fill:#F0FFF0,stroke:#90C695,stroke-width:1px
    style NS_DATA fill:#F5F0FF,stroke:#B0A0D4,stroke-width:1px
    style MANAGED fill:#FFFAF0,stroke:#D4B896,stroke-width:1px""",
    },
    {
        "id": "DIA-004",
        "title": "Event-Driven Data Flow",
        "type": "flowchart",
        "description": "Kafka event flow between services for eventual consistency",
        "mermaid_code": """flowchart LR
    subgraph PRODUCERS["Event Producers"]
        ORD["Order Service"]
        INV["Inventory Service"]
        CAT["Catalog Service"]
    end

    subgraph KAFKA["Kafka Topics"]
        T1["orders.created"]
        T2["orders.completed"]
        T3["inventory.updated"]
        T4["products.changed"]
    end

    subgraph CONSUMERS["Event Consumers"]
        INV2["Inventory\\nStock Deduction"]
        RECO["Recommendation\\nModel Update"]
        NOTIFY["Notification\\nEmail + Push"]
        ANALYTICS["Analytics\\nDashboard"]
    end

    ORD -->|order placed| T1
    ORD -->|payment confirmed| T2
    INV -->|stock changed| T3
    CAT -->|product updated| T4

    T1 --> INV2
    T1 --> NOTIFY
    T2 --> ANALYTICS
    T3 --> RECO
    T3 --> ANALYTICS
    T4 --> RECO

    style PRODUCERS fill:#E8F4FD,stroke:#7FB3D3,stroke-width:2px
    style KAFKA fill:#F5F0FF,stroke:#B0A0D4,stroke-width:2px
    style CONSUMERS fill:#F0FFF0,stroke:#90C695,stroke-width:2px""",
    },
    {
        "id": "DIA-005",
        "title": "Database Schema - Entity Relationship",
        "type": "er",
        "description": "Core database entities and relationships for ShopAI",
        "mermaid_code": """erDiagram
    USER ||--o{ ORDER : places
    USER ||--o{ REVIEW : writes
    USER ||--o{ CART : has
    USER {
        uuid id PK
        string email
        string password_hash
        string name
        string oauth_provider
        datetime created_at
    }

    VENDOR ||--o{ PRODUCT : sells
    VENDOR ||--o{ STOREFRONT : manages
    VENDOR {
        uuid id PK
        string company_name
        string contact_email
        float commission_rate
        string status
    }

    PRODUCT ||--o{ ORDER_ITEM : contains
    PRODUCT ||--o{ INVENTORY : tracked_in
    PRODUCT ||--o{ REVIEW : receives
    PRODUCT {
        uuid id PK
        string title
        text description
        decimal price
        string category
        uuid vendor_id FK
    }

    ORDER ||--|{ ORDER_ITEM : includes
    ORDER ||--o| PAYMENT : paid_by
    ORDER {
        uuid id PK
        uuid user_id FK
        decimal total
        string status
        datetime created_at
    }

    ORDER_ITEM {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        decimal unit_price
    }

    PAYMENT {
        uuid id PK
        uuid order_id FK
        string stripe_id
        decimal amount
        string status
    }

    INVENTORY {
        uuid id PK
        uuid product_id FK
        string warehouse
        int quantity
        int reserved
    }

    CART ||--|{ CART_ITEM : contains
    CART {
        uuid id PK
        uuid user_id FK
    }

    CART_ITEM {
        uuid id PK
        uuid cart_id FK
        uuid product_id FK
        int quantity
    }

    REVIEW {
        uuid id PK
        uuid user_id FK
        uuid product_id FK
        int rating
        text comment
    }

    STOREFRONT {
        uuid id PK
        uuid vendor_id FK
        string name
        string theme
        string custom_domain
    }""",
    },
]

p["architecture"]["diagrams"] = diagrams

with open(".rai/project.yaml", "w", encoding="utf-8") as f:
    yaml.dump(p, f, default_flow_style=False, allow_unicode=True, sort_keys=True)

print(f"Added {len(diagrams)} architecture diagrams to project.yaml")
