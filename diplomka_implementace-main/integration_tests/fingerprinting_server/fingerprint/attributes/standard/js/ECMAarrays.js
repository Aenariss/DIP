/*
#  JShelter is a browser extension which increases level
#  of security, anonymity and privacy of the user while browsing the
#  internet.
#
#  Copyright (C) 2022  Libor Polčák
#  Copyright (C) 2022  Martin Bednar
#  Copyright (C) 2020  Peter Hornak
#  Copyright (C) 2024  Jana Petranova
#
#  SPDX-License-Identifier: GPL-3.0-or-later
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/ 

BigInt.prototype.toJSON = function() { 
    return this.toString() + "n"; /* Used by deepEqual below, this generates an invalid JSON file but it does not matter for the test cases */ 
  }; 

function deepEqual(a, b) {
    try { 
        let jsona = JSON.stringify(a);
        let jsonb = JSON.stringify(b);
        if (a === b || jsona === jsonb) { /* Make the comparison better if you encounter problems with this approach */ 
            return true;
        } 
        else { 
            return false;
        } 
    } 
    catch (e) { 
        return "error" + e;
    } 
}

function arrayEqual(a, b) {
    function toArray(arr) {
        var resultArr = [];
        for (let i = 0; i < arr.length; ++i) {
            resultArr[i] = arr[i];
        }
        return resultArr;
    }
    var is_equal = deepEqual(toArray(a), toArray(b));
    return is_equal;
}

function test_crypto_getRandomValues (){

	var arrayUint32 = new Uint32Array(4);
    var arrayBigInt64 = new BigInt64Array(4);
    var arrayBigUint64 = new BigUint64Array(4);
    
	window.crypto.getRandomValues(arrayUint32);
    window.crypto.getRandomValues(arrayBigInt64);
    window.crypto.getRandomValues(arrayBigUint64);
	
    var cryptoRandom = {
        "arrayUint32": arrayUint32,
        "arrayBigInt64": arrayBigInt64,
        "arrayBigUint64": arrayBigUint64
    };

    return cryptoRandom;

}

function test_ArrayBufferViews(){
    let buffer = new ArrayBuffer(56);
    let typedArr = new Uint32Array(buffer, 16);
    typedArr.set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);

    var typedArrBuffer = deepEqual(typedArr.buffer, buffer);
    var typedArrByteOffset = deepEqual(typedArr.byteOffset, 16);
    var typedArrByteLenght = deepEqual(typedArr.byteLength, 40);

    var dataView = new DataView(buffer, 32);
    var dataWievBuffer = deepEqual(dataView.buffer, buffer);
    var dataViewByteOffset = deepEqual(dataView.byteOffset, 32);
    var dataViewByteLenght = deepEqual(dataView.byteLength, 24);

    var arrayBufferViews = {
        "typedArrBuffer": typedArrBuffer,
        "typedArrByteOffset": typedArrByteOffset,
        "typedArrByteLenght": typedArrByteLenght,

        "dataWievBuffer": dataWievBuffer,
        "dataViewByteOffset": dataViewByteOffset,
        "dataViewByteLenght": dataViewByteLenght
    }

    return arrayBufferViews;
}

function test_TypedArraysInit(){
    var typedArray = new Uint32Array([1, 100, 1000, 2, 200]);
    var typedArrayInt = arrayEqual(typedArray, [1, 100, 1000, 2, 200]);

    return typedArrayInt;
}

function test_TypedArraysParams32(){
    var typedArray = new Uint32Array([1, 100, 1000, 2, 200]);

    var bytesPerElement = deepEqual(typedArray.BYTES_PER_ELEMENT, 4);
    var typedArrayByteLenght = deepEqual((typedArray.length * typedArray.BYTES_PER_ELEMENT), typedArray.byteLength);
    var typedArrayLenght = deepEqual(typedArray.length, 5);
    var typedArrayByteOffset = deepEqual(typedArray.byteOffset, 0);

    var typedArraysParams32 = {
        "bytesPerElement": bytesPerElement,
        "typedArrayByteLenght": typedArrayByteLenght,
        "typedArrayLenght": typedArrayLenght,
        "typedArrayByteOffset": typedArrayByteOffset
    }

    return typedArraysParams32;

}

function test_TypedArraysInitByLength(){
    var num = 10**5;
    var typedArray = new Uint8Array(num);
    var typedArraysIntitByLenght = arrayEqual(typedArray, Array(num).fill(0));

    return typedArraysIntitByLenght;
}

function test_TypedArraysOverwriteElement(){
    var typedArray = new Uint32Array([1, 100, 1000, 2, 200]);
    typedArray[0] = 10;
    var typedArraysOverwriteElement = arrayEqual(typedArray, [10, 100, 1000, 2, 200]);
    return typedArraysOverwriteElement;
}

function test_TypedArraysOverwriteFull(){
    var typedArray = new Uint8Array(5);
    typedArray.set([1, 2, 3, 4, 5]);
    var typedArraysOverwriteFull = arrayEqual(typedArray, [1, 2, 3, 4, 5]);
    return typedArraysOverwriteFull;
}

function test_TypedArraysParams8(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);

    var bytesPerElement = deepEqual(typedArray.BYTES_PER_ELEMENT, 1);
    var arrayByteLenght = deepEqual(typedArray.length * typedArray.BYTES_PER_ELEMENT, typedArray.byteLength);
    var arrayLenght = deepEqual(typedArray.length, 5);
    var arrayByteOffset = deepEqual(typedArray.byteOffset, 0);

    var typedArrayParams8 = {
        "bytesPerElement": bytesPerElement,
        "arrayByteLenght": arrayByteLenght,
        "arrayLenght": arrayLenght,
        "arrayByteOffset": arrayByteOffset
    }

    return typedArrayParams8;
}

function test_TypedArrayFromBuffer(){
    var arrayBuffer = new ArrayBuffer(5);
    var typedArray  = new Uint8Array(arrayBuffer);

    typedArray.set([1, 2, 3, 4, 5]);

    var typedArrays = arrayEqual(typedArray, [1, 2, 3, 4, 5]);

    typedArray[0] = 100;

    var typedArraysChange = arrayEqual(typedArray, [100, 2, 3, 4, 5]);

    var bytesPerElement = deepEqual(typedArray.BYTES_PER_ELEMENT, 1);
    var arrayByteLenght = deepEqual(typedArray.length * typedArray.BYTES_PER_ELEMENT, typedArray.byteLength);
    var arrayLenght = deepEqual(typedArray.length, 5);
    var arrayByteOffset = deepEqual(typedArray.byteOffset, 0);

    var typedArrayFromBuffer = {
        "typedArrays": typedArrays,
        "typedArraysChange": typedArraysChange,

        "bytesPerElement": bytesPerElement,
        "arrayByteLenght": arrayByteLenght,
        "arrayLenght": arrayLenght,
        "arrayByteOffset":arrayByteOffset
        }

    return typedArrayFromBuffer;

}

function test_TypedArraysMethods_set(){
    var defaultVals = [1, 2, 3, 4, 5];
    var typedArray = new Uint8Array(5);
    typedArray.set(defaultVals);

    var typedArraysMethodsSet = arrayEqual(typedArray, defaultVals);

    return typedArraysMethodsSet;
}

function test_TypedArraysMethods_reverse(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    typedArray.reverse();
    var arrayReverse = arrayEqual(typedArray, [5, 4, 3, 2, 1]);

    return arrayReverse;
}

function test_TypedArraysMethods_sort(){
    var typedArray = new Uint8Array([5, 4, 3, 2, 1]);
    typedArray.sort();

    var typedArraysMethodsSet = arrayEqual(typedArray, [1, 2, 3, 4, 5]);
    return typedArraysMethodsSet;
}

function test_TypedArraysMethods_fill(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    typedArray.fill(10, 0, 2);

    var typedArraysMethodsFill = arrayEqual(typedArray, [10, 10, 3, 4, 5]);
    return typedArraysMethodsFill;
}

function test_TypedArraysMethods_copyWithin() {
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    typedArray.copyWithin(2, 0, 2);

    var typedArraysMethodsCopyWithin = arrayEqual(typedArray, [1, 2, 1, 2, 5]);
    return typedArraysMethodsCopyWithin;
}

function test_TypedArraysMethods_subarray() {
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    var sub = typedArray.subarray(0, 4);

    var subarrayEqual = arrayEqual(sub, [1, 2, 3, 4]);

    sub[0] = 1;
    
    var subsEqual = deepEqual(sub[0], typedArray[0]);

    var TypedArraysMethodsSubarray = {
        "subarrayEqual": subarrayEqual,
        "subsEqual": subsEqual
    }

    return TypedArraysMethodsSubarray;
}

function test_TypedArraysMethods_slice(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    var slice = typedArray.slice(0, 2);

    var arraysSlice = arrayEqual(slice, [1, 2]);

    slice[0] = 100;
    var sliceEqual = deepEqual(slice[0], 100);
    var arraysSliceRep = arrayEqual(typedArray, [1, 2, 3, 4, 5]);

    var typedArraysMethodsSlice = {
        "arraysSlice": arraysSlice,
        "sliceEqual": sliceEqual,
        "arraysSliceRep": arraysSliceRep
    }

    return typedArraysMethodsSlice;
}

function test_TypedArraysMethods_map(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    var map = typedArray.map(x => x * 2);

    var typedArraysMethodsMap = arrayEqual(map, [2, 4, 6, 8, 10]);
    return typedArraysMethodsMap;
}

function test_TypedArraysMethods_filter(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    var filter = typedArray.filter(x => x > 2);

    var arrayFilter = arrayEqual(filter, [3, 4, 5]);
    return arrayFilter;
}

function test_TypedArraysMethods_reduce(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    var reduce = typedArray.reduce(function (prev, curr) {
        return prev + curr;
    });

    var methodsReduce = deepEqual(reduce, 15);
    return methodsReduce;
}

function test_TypedArraysMethods_reduceR(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    reduceR = typedArray.reduce(function (prev, curr) {
        return prev + curr;
    });

    var methodsReduceR = deepEqual(reduceR, 15);
    return methodsReduceR;
}

function test_TypedArraysMethods_lastIndexOf(){
    var typedArray = new Uint8Array([10, 10, 10, 4, 5]);
    var methodsLastIndexOf = deepEqual(typedArray.lastIndexOf(10), 2);
    return methodsLastIndexOf;
}

function test_TypedArraysMethods_forEach(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    var forEachArr = [];
    typedArray.forEach(x => forEachArr.push(x));

    var methodsForEach = arrayEqual(forEachArr, [1, 2, 3, 4, 5]);

    return methodsForEach;
}

function test_TypedArraysMethods_find(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5])
    var find = typedArray.find(function (value, index, obj) {
        return value > 1;
    });

    var methodsFind = deepEqual(find, 2);
    return methodsFind;
}

function test_TypedArraysMethods_join(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    var methodsJoin = deepEqual(typedArray.join(), "1,2,3,4,5");

    return methodsJoin;
}



function test_TypedArraysMethods_entrieskeysvalues(){
    var typedArray = new Uint8Array([1, 2, 3, 4, 5]);
    var iter_entries = typedArray.entries()
    var iter_keys    = typedArray.keys();
    var iter_values  = typedArray.values();

    var nextArrays = arrayEqual(iter_entries.next().value, [0, 1]);

    var nextKey = deepEqual(iter_keys.next().value, 0);
    var nextItem = deepEqual(iter_values.next().value, 1);

    var arrayEntries = arrayEqual(iter_entries.next().value, [1, 2]);

    var nextKey2 = deepEqual(iter_keys.next().value, 1);
    var nextItem2 = deepEqual(iter_values.next().value, 2);

    var typedArraysMethodsEK = {
        "nextArrays": nextArrays,
        "nextKey": nextKey,
        "nextItem": nextItem,
        "arrayEntries": arrayEntries,
        "nextKey2": nextKey2,
        "nextItem2": nextItem2
    }

    return typedArraysMethodsEK;
}

function test_TypedArraysMethods_from(){
    var methodsFrom = arrayEqual(Uint8Array.from([1, 2, 3]), [1, 2, 3]);
    return methodsFrom;
}

function test_TypedArraysMethods_of(){
    var methodsOf = arrayEqual(Uint8Array.of(1, 2, 3, 4), [1, 2, 3, 4]);
    return methodsOf;
}

function test_DataViewInit(){
    var buff = new ArrayBuffer(16);
    var dataView_test_DataViewInit = new DataView(buff);

    var byteLength = deepEqual(dataView_test_DataViewInit.byteLength, 16);
    var byteOffset = deepEqual(dataView_test_DataViewInit.byteOffset, 0);
    var byteBuffer = deepEqual(dataView_test_DataViewInit.buffer, buff);

    dataView_test_DataViewInit = new DataView(buff, 4, 8);

    var newByteLenght = deepEqual(dataView_test_DataViewInit.byteLength, 8);
    var newByteOffset = deepEqual(dataView_test_DataViewInit.byteOffset, 4);

    var dataViewInit = {
        "byteLength": byteLength,
        "byteOffset": byteOffset,
        "byteBuffer": byteBuffer,
        "newByteLenght":newByteLenght,
        "newByteOffset":newByteOffset
    }

    return dataViewInit;


};

function test_DataViewAccessors(){
    buff = new ArrayBuffer(128);
    dataView = new DataView(buff);

    const DATA_VIEW_ACCESSORS = [
        ['getInt8', 'setInt8', "Number"],
        ['getInt16', 'setInt16', "Number"],
        ['getInt32', 'setInt32', "Number"],
        ['getUint8', 'setUint8', "Number"],
        ['getUint16', 'setUint16', "Number"],
        ['getUint32', 'setUint32', "Number"],
        ['getFloat32', 'setFloat32', "Number"],
        ['getFloat64', 'setFloat64', "Number"],
        ['getBigInt64', 'setBigInt64', "BigInt"],
        ['getBigUint64', 'setBigUint64', "BigInt"]
    ];
    
    var loopSetGet = [];

    let n = 1;
    for (let i = 0; i < DATA_VIEW_ACCESSORS.length; i++) {
        n += 10;
        const [getter, setter, t] = DATA_VIEW_ACCESSORS[i];   
        if (t == "Number") {
            dataView[setter](0, n);
            var isSet1 = deepEqual(dataView[getter](0), n); 
            loopSetGet.push(isSet1);

            dataView[setter](0, n, true);
            var isSet2 = deepEqual(dataView[getter](0, true), n); 
            loopSetGet.push(isSet2);
        }
        else {
            dataView[setter](0, BigInt(n));
            var isSet1 = deepEqual(dataView[getter](0), BigInt(n)); 
            loopSetGet.push(isSet1);

            dataView[setter](0, BigInt(n), true);
            var isSet2 = deepEqual(dataView[getter](0, true), BigInt(n)); 
            loopSetGet.push(isSet2);
        }
        
    }

    dataView.setFloat64(1, 123456.7891);
    var floatSet = deepEqual(dataView.getFloat64(1), 123456.7891);
    dataView.setInt32(2, -12345);
    var intSet = deepEqual(dataView.getInt32(2), -12345);
    dataView.setBigInt64(0, -1234567890123456789n);
    var bigSet = deepEqual(dataView.getBigInt64(0), -1234567890123456789n);
    
    

    var dataViewAccessrsRes = {
        "loopSetGet": loopSetGet,
        "floatSet": floatSet,
        "intSet": intSet,
        "bigSet": bigSet
    }
    return dataViewAccessrsRes;
}

function test_OneBufferMoreViews(){
    var aBuff = new ArrayBuffer(12);
    var typedArray = new Int8Array(aBuff);
    var dataView = new DataView(aBuff);
    typedArray[0] = 10;

    var moreViews = deepEqual(typedArray[0], dataView.getInt8(0));
    return moreViews
}

(function() {
    api.register("ECMAarrays", function () {
        try {
            var cryptoGetRandomValues = test_crypto_getRandomValues();

            var arrayBufferViews = test_ArrayBufferViews();
            var typedArraysInt = test_TypedArraysInit();
            var typedArraysParams32 = test_TypedArraysParams32();

            var typedArraysInitByLenght = test_TypedArraysInitByLength();
            var typedArraysOverwriteElement = test_TypedArraysOverwriteElement();
            var typedArraysOverwriteFull = test_TypedArraysOverwriteFull();

            var typedArraysParams8 = test_TypedArraysParams8();
            var typedArrayFromBuffer = test_TypedArrayFromBuffer();

            var typedArraysMethodsSet = test_TypedArraysMethods_set();
            var typedArraysMethodsReverse = test_TypedArraysMethods_reverse();

            var typedArraysMethodsSort = test_TypedArraysMethods_sort();
            var typedArraysMethodsFill = test_TypedArraysMethods_fill();

            var typedArraysMethodsCopyWithin = test_TypedArraysMethods_copyWithin();
            var typedArrayMethodsSubarray = test_TypedArraysMethods_subarray();

            var typedArraysMethodsSlice = test_TypedArraysMethods_slice();
            var typedArraysMethodsMap = test_TypedArraysMethods_map();

            var typedArrayMethodsFilter = test_TypedArraysMethods_filter();
            var typedArrayMethodsReduce = test_TypedArraysMethods_reduce();

            var typedArraysMethodsReduceR = test_TypedArraysMethods_reduceR();
            var typedArraysMethodsLastIndexOf = test_TypedArraysMethods_lastIndexOf();

            var typedArraysMethodsForEach = test_TypedArraysMethods_forEach();
            var typedArraysMethodsFind = test_TypedArraysMethods_find();

            var typedArraysMethodsJoin = test_TypedArraysMethods_join();
            var typedArraysMethodsEntriesKeysValues = test_TypedArraysMethods_entrieskeysvalues();

            var typedArrayMethodsFrom = test_TypedArraysMethods_from();
            var typedArrayMethodsOf = test_TypedArraysMethods_of();

            var dataViewInit = test_DataViewInit();
            var dataViewAccessors = test_DataViewAccessors();

            var oneBufferMoreViews = test_OneBufferMoreViews();

            const result = {
                "cryptoGetRandomValues": cryptoGetRandomValues,
                "arrayBufferViews": arrayBufferViews,
                "typedArraysInt": typedArraysInt,
                "typedArraysParams32": typedArraysParams32,
                "typedArraysInitByLenght": typedArraysInitByLenght,
                "typedArraysOverwriteElement":typedArraysOverwriteElement,
                "typedArraysOverwriteFull": typedArraysOverwriteFull,
                "typedArraysParams8": typedArraysParams8,
                "typedArrayFromBuffer": typedArrayFromBuffer,
                "typedArraysMethodsSet" : typedArraysMethodsSet,
                "typedArraysMethodsReverse": typedArraysMethodsReverse, 
                "typedArraysMethodsSort": typedArraysMethodsSort,
                "typedArraysMethodsFill": typedArraysMethodsFill,
                "typedArraysMethodsCopyWithin": typedArraysMethodsCopyWithin,
                "typedArrayMethodsSubarray": typedArrayMethodsSubarray,
                "typedArraysMethodsSlice": typedArraysMethodsSlice,
                "typedArraysMethodsMap": typedArraysMethodsMap,
                "typedArrayMethodsFilter": typedArrayMethodsFilter,
                "typedArrayMethodsReduce": typedArrayMethodsReduce, 
                "typedArraysMethodsReduceR": typedArraysMethodsReduceR,
                "typedArraysMethodsLastIndexOf" : typedArraysMethodsLastIndexOf,
                "typedArraysMethodsForEach": typedArraysMethodsForEach,
                "typedArraysMethodsFind": typedArraysMethodsFind,
                "typedArraysMethodsJoin": typedArraysMethodsJoin,
                "typedArraysMethodsEntriesKeysValues": typedArraysMethodsEntriesKeysValues,
                "typedArrayMethodsFrom": typedArrayMethodsFrom,
                "typedArrayMethodsOf": typedArrayMethodsOf,
                "dataViewInit": dataViewInit,
                "dataViewAccessors":dataViewAccessors,
                "oneBufferMoreViews": oneBufferMoreViews

            }
        
            return result;
        }
        catch(e) {
            return "js blocked";
        }
    });
})();
