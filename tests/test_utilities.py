#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Utilities for tests."""


def float_compare(x_val, y_val, precision=1e-6):
    '''Helper function to check that two numbers are equal within float precision.'''
    if y_val == 0:
        return x_val == 0
    if abs((x_val - y_val) / y_val) < precision:
        return True
    return False


def tuple_compare(x_tup, y_tup):
    '''Helper function to check that two tuples are equal within float precision.'''
    same = True
    for pair in zip(x_tup, y_tup):
        same &= float_compare(pair[0], pair[1])
    return same
