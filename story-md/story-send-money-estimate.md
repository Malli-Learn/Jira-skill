# Send Money Estimate
 
## Summary
Send Money Estimate
 
## Description
 
As a user, I want to estimate the total cost of sending money internationally before completing the transaction, so I can understand fees, exchange rates, and delivery options upfront.
 
The Send Money Estimate feature provides users with a comprehensive cost calculator for international money transfers. It allows users to preview all transfer details including fees, exchange rates, payment methods, and delivery options before committing to a transaction.
 
### Feature Components
 
#### 1. Amount Configuration ([EnterAmount.tsx](packages/WURNMobile/src/modules/send-money/estimate/screens/EnterAmount.tsx))
- Users can enter either send amount or receive amount
- Real-time currency conversion based on selected destination country
- Support for multiple currencies per destination
- Visual validation of transaction limits (minimum/maximum)
- Display of KYC-based sending limits
 
#### 2. **Estimate Details View** ([EstimateDetails.tsx](packages/WURNMobile/src/modules/send-money/estimate/screens/EstimateDetails.tsx))
 
**Transfer breakdown:**
- Send amount
- Transfer fees (with promotional discounts if applicable)
- Exchange rate (with FX rate alerts)
- Receiver gets amount
- Total pay amount
 
**Payment method selection (Pay-In):**
- Debit/credit cards
- Bank accounts
- Cash in-store
- Bank transfers
- Apple Pay (mobile)
- Wallet options
 
**Delivery method selection (Pay-Out):**
- Cash pickup at agent locations
- Bank account deposit
- Mobile wallet transfer
- Debit card deposit
- Delivery speed indicators (minutes, hours, days)
 
#### 3. **Pricing Engine Integration** ([PriceProducts.ts](packages/common/src/modules/send-money/estimate/helpers/PriceProducts.ts))
- Cloud-based pricing API integration
- Real-time fee calculation based on:
  - Origin/destination countries
  - Payment method
  - Payout method  
  - Transfer amount
  - User type (guest vs. registered)
  - Promotional campaigns
- Support for promotional pricing and discounts
 
#### 4. **Key Features**
- Country and currency selection
- Receiver selection (saved receivers or new)
- Promotional code application
- FX rate notifications and alerts
- Transaction limit enforcement
- Compliance and regulatory checks
- Split fee display (if enabled)
- Reward points integration (My WU)
- Interstitial content display
- Recurring transfer scheduling
 
### Technical Architecture
 
**State Management:**
- Redux reducers for estimate data
- Saga middleware for async API calls
- Selectors for derived state calculations
 
**API Integration:**
- GraphQL queries for pricing
- RESTful endpoints for limits and compliance
- Cloud pricing service integration
 
**Platforms:**
- Web (Next.js)
- Mobile (React Native - iOS/Android)  
- Kiosk
 
### User Flow
1. User selects destination country
2. User enters send/receive amount
3. System fetches available payment and payout options
4. User selects preferred pay-in method
5. User selects preferred payout method
6. System displays complete cost breakdown
7. User can apply promo codes or rewards
8. User proceeds to receiver selection and review
 
### Acceptance Criteria
- [ ] Users can toggle between entering send amount or receive amount
- [ ] Exchange rates update in real-time when amounts change
- [ ] All fees are clearly displayed and itemized
- [ ] Payment methods are filtered based on country and amount
- [ ] Delivery speed is accurately displayed for each payout option
- [ ] Promotional discounts are correctly applied and displayed
- [ ] Transaction limits are enforced with appropriate error messages
- [ ] FX rate alerts are triggered when applicable
- [ ] Users can save estimate and resume later
- [ ] Estimate data persists across navigation
 
### Dependencies
- Pricing API service
- Country configuration service
- Payment method availability service
- FX rate service
- User profile and KYC status
- Rewards/loyalty system integration
 
### Related Files
- **Common Module:**
  - Actions: `packages/common/src/modules/send-money/estimate/actions/Actions.ts`
  - Reducers: `packages/common/src/modules/send-money/estimate/reducers/Reducers.ts`
  - Sagas: `packages/common/src/modules/send-money/estimate/sagas/Sagas.ts`
  - Selectors: `packages/common/src/modules/send-money/estimate/selectors/Selector.ts`
  - Helpers: `packages/common/src/modules/send-money/estimate/helpers/`
  - Utils: `packages/common/src/modules/send-money/estimate/utils/`
 
- **Mobile Screens:**
  - `packages/WURNMobile/src/modules/send-money/estimate/screens/EnterAmount.tsx`
  - `packages/WURNMobile/src/modules/send-money/estimate/screens/EstimateDetails.tsx`
 
- **Web Screens:**
  - `packages/web/src/pages/[countryCode]/[langCode]/[partnerName]/send-money/estimate-details.tsx`
  - `packages/web/src/pages/[countryCode]/[langCode]/[partnerName]/send-money/enter-amount.tsx`
 
- **Routes:**
  - `/send-money/estimate` (SMEstimate)
  - `/send-money/estimate-details` (SMEstimateDetails)
 
---
 
 
 