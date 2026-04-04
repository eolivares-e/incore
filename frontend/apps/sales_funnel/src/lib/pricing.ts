import type { RiskLevel, PriceEstimate } from '@/types'

// Base premiums per risk level — matches backend seed data for auto insurance
const BASE_PREMIUMS: Record<RiskLevel, number> = {
  low: 500,
  medium: 900,
  high: 1400,
  very_high: 2000,
}

function getAge(dateOfBirth: string): number {
  const dob = new Date(dateOfBirth)
  const today = new Date()
  let age = today.getFullYear() - dob.getFullYear()
  const m = today.getMonth() - dob.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--
  return age
}

function getRiskLevel(score: number): RiskLevel {
  if (score <= 30) return 'low'
  if (score <= 50) return 'medium'
  if (score <= 70) return 'high'
  return 'very_high'
}

export function estimatePremium(
  dateOfBirth: string,
  coverageAmount: number
): PriceEstimate {
  const age = getAge(dateOfBirth)

  // Risk score — mirrors backend PricingEngine.calculate_risk_level()
  let riskScore = 0

  // Age factors
  let ageRiskScore = 0
  let ageReason = 'standard'
  if (age < 25) {
    ageRiskScore = 20
    ageReason = 'young_driver'
  } else if (age > 70) {
    ageRiskScore = 20
    ageReason = 'senior_driver'
  }
  riskScore += ageRiskScore

  // Coverage factors
  let coverageRiskScore = 0
  if (coverageAmount > 5_000_000) {
    coverageRiskScore = 30
  } else if (coverageAmount > 1_000_000) {
    coverageRiskScore = 15
  }
  riskScore += coverageRiskScore

  // Auto policy type adjustment
  riskScore += 10

  const riskLevel = getRiskLevel(riskScore)
  const basePremium = BASE_PREMIUMS[riskLevel]

  // Premium formula — mirrors backend PricingEngine.calculate_premium()
  const coverageAdjustment = (coverageAmount / 100_000) * 0.05 * basePremium
  let annualPremium = basePremium + coverageAdjustment

  let ageMultiplier = 1.0
  if (ageReason === 'young_driver') ageMultiplier = 1.2
  else if (ageReason === 'senior_driver') ageMultiplier = 1.15

  annualPremium = annualPremium * ageMultiplier

  return {
    annual_premium: Math.round(annualPremium * 100) / 100,
    monthly_premium: Math.round((annualPremium / 12) * 100) / 100,
    risk_level: riskLevel,
    risk_score: riskScore,
    breakdown: {
      base_premium: basePremium,
      coverage_adjustment: Math.round(coverageAdjustment * 100) / 100,
      age_multiplier: ageMultiplier,
      age_reason: ageReason,
    },
  }
}
