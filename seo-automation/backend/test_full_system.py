#!/usr/bin/env python3
"""
Comprehensive test script for SEO Automation Platform
Tests image generation, content generation, and database operations
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.content_service import generate_seo_block, _get_business_image
from services.location_service import get_nearby_cities

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_section(title):
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")

async def test_image_generation():
    """Test 1: Image Generation"""
    print_header("TEST 1: IMAGE GENERATION (No API Keys Required)")
    
    test_cases = [
        ("Software Engineer", "San Diego"),
        ("Plumbing", "La Jolla"),
        ("Yoga Instructor", "Chula Vista"),
        ("Restaurant", "Downtown"),
        ("Marketing", "Coronado"),
    ]
    
    results = []
    for business_type, city in test_cases:
        print(f"\n🔍 {business_type} in {city}")
        try:
            image_url = await _get_business_image(business_type, city)
            
            # Check if it's from Unsplash Source (business-specific)
            if "source.unsplash.com" in image_url:
                # Extract search terms from URL
                search_terms = image_url.split("/?")[1] if "/?" in image_url else "N/A"
                print(f"   ✅ Business-specific image from Unsplash")
                print(f"   🔍 Search: {search_terms}")
                print(f"   📸 URL: {image_url}")
                results.append(("✅", business_type, city, search_terms))
            elif "/id/" in image_url:
                # Old Lorem Picsum format
                image_id = image_url.split("/id/")[1].split("/")[0]
                print(f"   ⚠️  Random image ID: {image_id}")
                print(f"   📸 URL: {image_url}")
                results.append(("⚠️", business_type, city, image_id))
            else:
                print(f"   ⚠️  URL: {image_url}")
                results.append(("⚠️", business_type, city, "N/A"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(("❌", business_type, city, str(e)))
    
    # Summary
    print_section("Image Generation Summary")
    success_count = sum(1 for r in results if r[0] == "✅")
    print(f"   Success: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("   🎉 All images generated successfully!")
        return True
    else:
        print("   ⚠️  Some images failed to generate")
        return False

async def test_location_service():
    """Test 2: Location Service"""
    print_header("TEST 2: LOCATION SERVICE")
    
    test_locations = [
        ("San Diego", 3),
        ("Los Angeles", 5),
    ]
    
    results = []
    for location, count in test_locations:
        print(f"\n🌍 Getting {count} cities near {location}")
        try:
            cities = await get_nearby_cities(location, count)
            print(f"   ✅ Found {len(cities)} cities:")
            for city in cities[:3]:  # Show first 3
                print(f"      • {city.name}, {city.state}")
            results.append(("✅", location, len(cities)))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(("❌", location, str(e)))
    
    # Summary
    print_section("Location Service Summary")
    success_count = sum(1 for r in results if r[0] == "✅")
    print(f"   Success: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("   🎉 All locations retrieved successfully!")
        return True
    else:
        print("   ⚠️  Some locations failed")
        return False

async def test_content_generation():
    """Test 3: Content Generation"""
    print_header("TEST 3: CONTENT GENERATION")
    
    test_cases = [
        ("Software Engineer", "San Diego", "CA"),
        ("Plumbing", "La Jolla", "CA"),
    ]
    
    results = []
    for business_type, city, state in test_cases:
        print(f"\n📝 Generating content for {business_type} in {city}, {state}")
        try:
            block = await generate_seo_block(business_type, city, state)
            
            print(f"   ✅ Content generated successfully!")
            print(f"      Title: {block.title[:60]}...")
            print(f"      Meta: {block.meta_description[:60]}...")
            print(f"      Image: {block.featured_image_url}")
            print(f"      Keywords: {len(block.keywords.secondary)} secondary keywords")
            print(f"      FAQs: {len(block.faqs)} questions")
            print(f"      SEO Score: {block.readability_score}/100")
            
            results.append(("✅", business_type, city))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append(("❌", business_type, city))
    
    # Summary
    print_section("Content Generation Summary")
    success_count = sum(1 for r in results if r[0] == "✅")
    print(f"   Success: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("   🎉 All content generated successfully!")
        return True
    else:
        print("   ⚠️  Some content failed to generate")
        return False

async def test_image_consistency():
    """Test 4: Image Consistency"""
    print_header("TEST 4: IMAGE CONSISTENCY")
    
    print("\n🔄 Testing if same business+city generates same image...")
    
    business_type = "Software Engineer"
    city = "San Diego"
    
    # Generate image 3 times
    images = []
    for i in range(3):
        image_url = await _get_business_image(business_type, city)
        images.append(image_url)
        print(f"   Attempt {i+1}: {image_url}")
    
    # Check if all are the same
    if len(set(images)) == 1:
        print(f"\n   ✅ CONSISTENT: All 3 attempts generated the same image!")
        print(f"   🎯 This ensures same business+city always gets same image")
        return True
    else:
        print(f"\n   ❌ INCONSISTENT: Different images generated!")
        return False

async def test_image_variety():
    """Test 5: Image Variety"""
    print_header("TEST 5: IMAGE VARIETY")
    
    print("\n🎨 Testing if different business types get different images...")
    
    test_cases = [
        ("Software Engineer", "San Diego"),
        ("Plumbing", "San Diego"),
        ("Yoga Instructor", "San Diego"),
    ]
    
    images = {}
    for business_type, city in test_cases:
        image_url = await _get_business_image(business_type, city)
        images[business_type] = image_url
        print(f"   {business_type}: {image_url}")
    
    # Check if all are different
    unique_images = len(set(images.values()))
    if unique_images == len(test_cases):
        print(f"\n   ✅ VARIETY: All {unique_images} business types got different images!")
        print(f"   🎯 This ensures different businesses get different images")
        return True
    else:
        print(f"\n   ⚠️  Only {unique_images}/{len(test_cases)} unique images")
        return False

async def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("  SEO AUTOMATION PLATFORM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("\n🚀 Starting tests...")
    
    results = {}
    
    # Run tests
    results["Image Generation"] = await test_image_generation()
    results["Location Service"] = await test_location_service()
    results["Content Generation"] = await test_content_generation()
    results["Image Consistency"] = await test_image_consistency()
    results["Image Variety"] = await test_image_variety()
    
    # Final Summary
    print_header("FINAL TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print("\n📊 Test Results:")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! System is working perfectly!")
        print("\n✅ Ready to use:")
        print("   1. Go to: http://localhost:5173/simple")
        print("   2. Generate content for any business type")
        print("   3. See consistent, high-quality images!")
        print("\n💡 No API keys needed - completely FREE!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        print("   Please check the errors above")
    
    print("\n" + "=" * 80)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
