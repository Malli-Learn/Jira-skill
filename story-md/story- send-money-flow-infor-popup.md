# Story 2: Send Money Flow - Information Pop-up
 
 
## Summary
Send Money Flow - Information Pop-up
 
## Description
 
As a user, I want to receive contextual information pop-ups during the send money flow, so I can understand important details about payment methods, delivery options, and transaction requirements.
 
The **Information Pop-up** feature displays contextual modals and interstitial screens throughout the send money journey to educate users about transaction details, requirements, and important notices.
 
### Feature Components
 
#### 1. **Interstitial Screen Management**
- Displays informational content between major flow transitions
- Triggered based on transaction conditions and user actions
- Managed through Redux state (`estimateInterstitialScreen`)
- Content configuration driven by feature flags
 
#### 2. **Pop-up Types**
 
**Payment Method Information:**
- Bank transfer instructions and requirements
- Card payment disclaimers
- Cash payment location finder
- Digital wallet setup instructions
 
**Delivery Method Information:**
- D2B (Direct to Bank) service disclaimers with delivery time estimates
- Cash pickup requirements and agent location info
- Mobile wallet service details
- Debit card deposit information
 
**Transaction Requirements:**
- KYC/ID verification prompts
- Document upload requirements
- Additional information needed alerts
- Compliance and regulatory notices
 
**Service Limitations:**
- Transaction limit warnings
- Service availability notifications
- Bank operating hours and holidays
- Country-specific restrictions
 
#### 3. **Content Examples** (from staticcontent.json)
 
**D2B Service Disclaimers:**
- **India (IN):** "Funds generally take minutes to reach a recipient's bank account in Kotak Mahindra Bank, YES Bank, Union Bank of India, Federal Bank, Punjab National Bank, Bank of Baroda and ICICI Bank..."
- **Indonesia (ID):** "Funds of up to IDR 10,000,000 per transaction generally take minutes to reach a recipient's bank account..."
- **Philippines (PH):** "Funds generally take minutes to reach a recipient's bank account, but funds sent to first-time Bank of the Philippines Islands receivers may take up to 2 hours..."
 
**Additional Info Pop-ups:**
- Receiver information validation
- Address completion requirements
- Bank account verification
- Payment method change confirmations
 
#### 4. **Display Triggers**
- User selects specific payment/payout method
- Transaction amount exceeds certain thresholds
- First-time user for specific corridor
- Regulatory requirements for destination country
- Service outage or maintenance notices
- Promotional campaign information
 
#### 5. **Technical Implementation**
 
**State Management:**
```typescript
estimateInterstitialScreen: {
  showFTC: boolean,        // Federal Trade Commission notice
  showBank: boolean,       // Bank-specific information
  showCash: boolean,       // Cash pickup information
  showCard: boolean,       // Card payment information
  showAdditionalInfo: boolean
}
```
 
**Actions:**
- `SM_SHOW_INTERSTITIAL_CONTENT` - Display interstitial screen
- `showInterstitialContent()` - Trigger pop-up display
- `updateSendReceiveAmount()` - May trigger info display
 
**Saga Workers:**
- `showInterstitialContentWorkerSaga` - Manages interstitial display logic
- Checks feature flags and transaction state
- Determines which pop-up to show based on context
 
### User Flow
1. User proceeds through send money flow
2. System detects condition requiring information display
3. Pop-up/interstitial screen appears with relevant content
4. User reads information and acknowledges (Continue/OK button)
5. User proceeds to next step in the flow
 
### Acceptance Criteria
- [ ] Pop-ups display at appropriate points in the flow
- [ ] Content is dynamically loaded based on country, payment method, and payout method
- [ ] Users can dismiss or acknowledge pop-ups
- [ ] Pop-ups don't block critical user actions unnecessarily
- [ ] Content is localized for user's language
- [ ] Pop-ups track user acknowledgment (analytics)
- [ ] Different pop-up types can be combined or sequenced
- [ ] Feature flags control which pop-ups are shown
- [ ] Pop-ups are accessible (screen reader support)
- [ ] Pop-ups work on web, iOS, and Android
 
### Dependencies
- Feature flag configuration (`getFeaturesConfig()`)
- Static content JSON (country-specific disclaimers)
- Redux state management
- Navigation system integration
- Analytics tracking
 
### Related Files
- Actions: `common/src/modules/send-money/estimate/actions/Actions.ts`
- Reducers: `common/src/modules/send-money/estimate/reducers/Reducers.ts`
- Sagas: `common/src/modules/send-money/estimate/sagas/Sagas.ts`
- Content: `packages/ConfigFiles/siteconfig/content/*/staticcontent.json`
 
---
 
 
 