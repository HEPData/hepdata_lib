#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Utilities for tests."""


def float_compare(x_val, y_val):
    '''Helper function to check that two numbers are equal within float precision.'''
    if y_val == 0:
        return x_val == 0
    if abs((x_val - y_val) / y_val) < 1e-8:
        return True
    return False


def tuple_compare(x_tup, y_tup):
    '''Helper function to check that two tuples are equal within float precision.'''
    return float_compare(x_tup[0], y_tup[0]) and float_compare(x_tup[1], y_tup[1])
