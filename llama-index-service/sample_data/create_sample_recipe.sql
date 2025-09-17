-- This script creates a sample Recipe table and populates it with manufacturing recipe data
-- Run this against the manufacturing database to create sample data for RAG indexing

-- Create the Recipe table if it doesn't exist
CREATE TABLE IF NOT EXISTS public."Recipe" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(100) NOT NULL,
    grain_bill TEXT,
    mash_temperature DECIMAL(5,2),
    fermentation_time INTEGER, -- In hours
    distillation_notes TEXT,
    aging_requirements TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample manufacturing recipes
INSERT INTO public."Recipe" (name, description, type, grain_bill, mash_temperature, fermentation_time, distillation_notes, aging_requirements)
VALUES 
('Kentucky Straight Bourbon', 'A traditional Kentucky-style bourbon with rich corn character and subtle rye spice.', 'Bourbon', '70% corn, 15% rye, 15% malted barley', 65.5, 72, 'Double distillation with first distillation to 40% ABV and second to 65-70% ABV. Collect hearts from 75-120°C.', 'Minimum 2 years in new charred oak barrels.'),

('Tennessee Whiskey', 'Smooth Tennessee whiskey with maple and charcoal notes from the Lincoln County Process.', 'Tennessee Whiskey', '80% corn, 8% rye, 12% malted barley', 64.0, 96, 'Double distillation followed by charcoal filtration through sugar maple charcoal.', 'Minimum 4 years in new charred oak barrels.'),

('High Rye Bourbon', 'Spicy high-rye bourbon with bold character and plenty of baking spice notes.', 'Bourbon', '60% corn, 35% rye, 5% malted barley', 67.0, 84, 'Copper pot still distillation with slow collection of hearts for maximum flavor.', 'Minimum 5 years in #3 char new oak barrels.'),

('Traditional Rye Whiskey', 'A classic Pennsylvania-style rye whiskey with bold spice and fruit notes.', 'Rye Whiskey', '95% rye, 5% malted barley', 63.0, 72, 'Double distillation in copper pot stills. Spirit cut begins at 68% ABV and ends at 75% ABV.', 'Minimum 2 years in new charred oak barrels.'),

('Wheated Bourbon', 'Smooth and sweet wheated bourbon with notes of caramel, vanilla, and honey.', 'Bourbon', '70% corn, 20% wheat, 10% malted barley', 62.0, 96, 'Double distillation with very careful hearts cut at 65-70% ABV.', 'Minimum 6 years in new charred oak barrels.'),

('Single Malt Whiskey', 'American single malt whiskey with notes of honey, toasted malt, and light fruit.', 'Single Malt', '100% malted barley', 65.0, 72, 'Double copper pot distillation with extended foreshots run to eliminate heavy sulphur compounds.', 'Minimum 3 years in ex-bourbon barrels.'),

('Corn Whiskey', 'Traditional corn whiskey with sweet corn notes and light oak influence.', 'Corn Whiskey', '85% corn, 15% malted barley', 68.0, 60, 'Single distillation to retain corn character. Spirit collected at 65-70% ABV.', 'Minimum 6 months in used oak barrels.'),

('Four Grain Bourbon', 'Complex bourbon using all four traditional whiskey grains for a layered flavor profile.', 'Bourbon', '60% corn, 15% rye, 15% wheat, 10% malted barley', 64.5, 84, 'Double distillation with extended heads and tails cuts for a clean spirit.', 'Minimum 4 years in new charred oak barrels, finished in port wine barrels.'),

('Barrel Proof Rye', 'Full-strength rye whiskey bottled directly from the barrel with no dilution.', 'Rye Whiskey', '80% rye, 20% malted barley', 66.0, 96, 'Pot still distillation with careful hearts cut to retain maximum rye spice character.', 'Minimum 7 years in new charred oak barrels with no dilution before bottling.'),

('Smoked Malt Whiskey', 'Peated American whiskey with smoky and savory notes balanced by sweetness.', 'Single Malt', '80% peated malted barley, 20% unpeated malted barley', 63.5, 72, 'Double distillation with extended foreshots and heads cut to control phenolic compounds.', 'Minimum 5 years in ex-bourbon barrels with 6 month finish in Oloroso Sherry casks.'); 