// Copyright 2015-2018 the openage authors. See copying.md for legal info.

#pragma once

#include <cstdint>
#include <vector>
#include <map>

#include <eigen3/Eigen/Dense>

#include "resources/mesh_data.h"
#include "../error/error.h"


namespace openage {
namespace renderer {

class UniformInput;
class Texture2d;

class ShaderProgram {
public:
	virtual ~ShaderProgram() = default;

	// Template dispatches for uniform variable setting.
	void update_uniform_input(UniformInput*) {}

	void update_uniform_input(UniformInput* input, const char* unif, int32_t val) {
		this->set_i32(input, unif, val);
	}

	void update_uniform_input(UniformInput* input, const char* unif, uint32_t val) {
		this->set_u32(input, unif, val);
	}

	void update_uniform_input(UniformInput* input, const char* unif, float val) {
		this->set_f32(input, unif, val);
	}

	void update_uniform_input(UniformInput* input, const char* unif, double val) {
		this->set_f64(input, unif, val);
	}

	void update_uniform_input(UniformInput* input, const char* unif, Eigen::Vector2f const& val) {
		this->set_v2f32(input, unif, val);
	}

	void update_uniform_input(UniformInput* input, const char* unif, Eigen::Vector3f const& val) {
		this->set_v3f32(input, unif, val);
	}

	void update_uniform_input(UniformInput* input, const char* unif, Eigen::Vector4f const& val) {
		this->set_v4f32(input, unif, val);
	}

	void update_uniform_input(UniformInput* input, const char* unif, Texture2d const* val) {
		this->set_tex(input, unif, val);
	}

	void update_uniform_input(UniformInput* input, const char* unif, Texture2d* val) {
		this->set_tex(input, unif, val);
	}

	void update_uniform_input(UniformInput* input, const char* unif, Eigen::Matrix4f const& val) {
		this->set_m4f32(input, unif, val);
	}

	template<typename T>
	void update_uniform_input(UniformInput*, const char* unif, T) {
		throw Error(MSG(err) << "Tried to set uniform " << unif << " using unknown type.");
	}

	/// Returns whether the shader program contains a uniform variable with the given name.
	virtual bool has_uniform(const char* unif) = 0;

	/// Creates a new uniform input (a binding of uniform names to values) for this shader
	/// and optionally sets some uniform values. To do that, just pass two arguments -
	/// - a string literal and the value for that uniform for any uniform you want to set.
	/// For example new_uniform_input("color", { 0.5, 0.5, 0.5, 1.0 }, "num", 5) will set
	/// "color" to { 0.5, 0.5, 0.5, 0.5 } and "num" to 5. Types are important here and a type
	/// mismatch between the uniform variable and the input might result in an error.
	template<typename... Ts>
	std::unique_ptr<UniformInput> new_uniform_input(Ts... vals) {
		auto input = this->new_unif_in();
		this->update_uniform_input(input.get(), vals...);
		return input;
	}

	/// Updates the given uniform input with new uniform values similarly to new_uniform_input.
	/// For example, update_uniform_input(in, "awesome", true) will set the "awesome" uniform
	/// in addition to whatever values were in the uniform input before.
	template<typename T, typename... Ts>
	void update_uniform_input(UniformInput* input, const char* unif, T val, Ts... vals) {
		this->update_uniform_input(input, unif, val);
		this->update_uniform_input(input, vals...);
	}

	/// Returns a list of _active_ vertex attributes in the shader program. Active attributes
	/// are those which have an effect on the shader output, meaning they are included in the
	/// output calculation and are not unused. Inactive attributes may or may not be present
	/// in the list - in particular, in the OpenGL implementation they will most likely be missing.
	/// The returned value is a map from the attribute location to its type. Locations need not
	/// be consecutive.
	virtual std::map<size_t, resources::vertex_input_t> vertex_attributes() const = 0;

protected:
	// Virtual dispatches to the actual shader program implementation.
	virtual std::unique_ptr<UniformInput> new_unif_in() = 0;
	virtual void set_i32(UniformInput*, const char*, int32_t) = 0;
	virtual void set_u32(UniformInput*, const char*, uint32_t) = 0;
	virtual void set_f32(UniformInput*, const char*, float) = 0;
	virtual void set_f64(UniformInput*, const char*, double) = 0;
	virtual void set_v2f32(UniformInput*, const char*, Eigen::Vector2f const&) = 0;
	virtual void set_v3f32(UniformInput*, const char*, Eigen::Vector3f const&) = 0;
	virtual void set_v4f32(UniformInput*, const char*, Eigen::Vector4f const&) = 0;
	virtual void set_m4f32(UniformInput*, const char*, Eigen::Matrix4f const&) = 0;
	virtual void set_tex(UniformInput*, const char*, Texture2d const*) = 0;
};

}}
