# Ec2 Requirements

- Instance:
- Storage:
- ssh client private-key (if possible)

## t2.small

Family: t2

- 1 vCPU
- 2GiB memory

## t3.small

Family: t3

- 2 vCPU
- 2 GiB memory

# On-demand Pricing for us-east-1 Linux instance

| Instance Name | On-Demand Hourly Rate | vCPU | Memory  | Storage  | Network Performance  |
|--------------|----------------------|------|---------|----------|----------------------|
| t2.small     | $0.023               | 1    | 2 GiB   | EBS Only | Low to Moderate     |
| t3.small     | $0.0208              | 2    | 2 GiB   | EBS Only | Up to 5 Gigabit     |

# Reserved instance prices: for term 12 months to 36 months

## t2.small

| Seller | Term Length | Effective Rate | Upfront Price | Hourly Rate | Payment Option  | Offering Class | Quantity Available | Desired Quantity | Normalized Units per Hour |
|--------|------------|----------------|---------------|-------------|-----------------|----------------|--------------------|----------------|--------------------------|
| AWS    | 36 month   | $0.009         | $229.00       | $0.00       | All upfront     | Standard       | Unlimited          | 1              | -                        |
| AWS    | 36 month   | $0.010         | $275.00       | $0.00       | All upfront     | Convertible    | Unlimited          | 1              | -                        |
| AWS    | 36 month   | $0.010         | $0.00         | $0.01       | No upfront      | Standard       | Unlimited          | 1              | -                        |
| AWS    | 36 month   | $0.012         | $0.00         | $0.0115     | No upfront      | Convertible    | Unlimited          | 1              | -                        |
| AWS    | 36 month   | $0.009         | $122.00       | $0.0046     | Partial upfront | Standard       | Unlimited          | 1              | -                        |
| AWS    | 36 month   | $0.011         | $140.00       | $0.0053     | Partial upfront | Convertible    | Unlimited          | 1              | -                        |

## t3.small

| Provider   | Term Length | Hourly Rate | Upfront Cost | Recurring Cost | Payment Option  | Type       | Performance | Quantity |
|------------|------------|-------------|--------------|----------------|----------------|------------|-------------|----------|
| AWS        | 36 month   | $0.008      | $206.00      | $0.00          | All upfront    | Standard   | Unlimited   | 1        |
| AWS        | 36 month   | $0.009      | $246.00      | $0.00          | All upfront    | Convertible | Unlimited  | 1        |
| AWS        | 36 month   | $0.009      | $0.00        | $0.009         | No upfront     | Standard   | Unlimited   | 1        |
| AWS        | 36 month   | $0.010      | $0.00        | $0.0103        | No upfront     | Convertible | Unlimited  | 1        |
| AWS        | 36 month   | $0.008      | $109.00      | $0.0042        | Partial upfront | Standard  | Unlimited   | 1        |
| AWS        | 36 month   | $0.010      | $126.00      | $0.0048        | Partial upfront | Convertible | Unlimited | 1        |
| 3rd party  | 34 month   | $0.008      | $200.00      | $0.00          | All upfront    | Standard   | 1          | 1        |
