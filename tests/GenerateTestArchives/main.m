//
//  main.m
//  GenerateTestArchives
//
//  Created by Nickolas Pohilets on 01/12/2017.
//  Copyright © 2017 Example.com. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface XXCustomObject: NSObject<NSCoding>

@property(nonatomic, readwrite, copy) NSString* foo;
@property(nonatomic, readwrite) NSInteger bar;

@end

@implementation XXCustomObject

- (instancetype)initWithCoder:(NSCoder *)aDecoder {
    if (self = [super init]) {
        _foo = [aDecoder decodeObjectForKey:@"foo"];
        _bar = [aDecoder decodeIntegerForKey:@"bar"];
    }
    return self;
}

- (void)encodeWithCoder:(NSCoder *)aCoder {
    [aCoder encodeObject:_foo forKey:@"foo"];
    [aCoder encodeInteger:_bar forKey:@"bar"];
}

@end

void SaveObject(NSString* name, id object) {
    NSString* path = [NSString stringWithUTF8String:__FILE__];
    path = [path stringByAppendingPathComponent:@"../../fixture_data"];
    name = [name stringByAppendingString:@"_archive.plist"];
    path = [path stringByAppendingPathComponent:name];
    path = [path stringByStandardizingPath];
    BOOL ok = [NSKeyedArchiver archiveRootObject:object toFile:path];
    NSCAssert(ok, @"Failed to save the object %@ to %@", object, path);
}

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        SaveObject(@"opaque", ({
            XXCustomObject* obj = [XXCustomObject new];
            obj.foo = @"abc";
            obj.bar = 42;
            obj;
        }));
        SaveObject(@"recursive_array", ({
            NSMutableArray* x1 = [NSMutableArray new];
            NSArray* x2 = @[ x1 ];
            [x1 addObject:x2];
            x2;
        }));
        SaveObject(@"recursive_dict", ({
            NSMutableDictionary* x1 = [NSMutableDictionary new];
            NSDictionary* x2 = @{ @"foo": x1 };
            [x1 setObject:x2 forKey:@"bar"];
            x2;
        }));
        SaveObject(@"data", [NSData dataWithBytes:"\xCA\xFE\xBA\xBE\x00\x01\x02\x03" length:8]);
        SaveObject(@"mutable_data", [NSMutableData dataWithBytes:"\xCA\xFE\xBA\xBE\x00\x01\x02\x03" length:8]);
        SaveObject(@"index_set", [NSIndexSet indexSetWithIndexesInRange:NSMakeRange(3, 213)]);
        SaveObject(@"mutable_index_set", ({
            NSMutableIndexSet* set = [NSMutableIndexSet new];
            [set addIndexesInRange:NSMakeRange(3, 8)];
            [set addIndexesInRange:NSMakeRange(35, 12)];
            [set addIndexesInRange:NSMakeRange(80234, 2346)];
            set;
        }));
        SaveObject(@"index_path", ({
            static NSUInteger const indices[] = {3, 4, 9};
            [NSIndexPath indexPathWithIndexes:indices length:3];
        }));
    }
    return 0;
}
