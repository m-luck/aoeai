// Copyright 2015-2018 the openage authors. See copying.md for legal info.

#include "logsource.h"

#include "../util/compiler.h"

#include "logsink.h"
#include "stdout_logsink.h"

namespace openage {
namespace log {


LogSource::LogSource()
	:
	logger_id{LogSource::get_unique_logger_id()} {}


void LogSource::log(const message &msg) {
	// ensure that the global stdoutsink has been constructed
	// (and thus at least one sink exists).
	global_stdoutsink();

	LogSinkList::instance().log(msg, this);
}


size_t LogSource::get_unique_logger_id() {
	// Strictly-monotonically increasing counter.
	static std::atomic<size_t> ctr{0};

	return ctr++;
}


}} // namespace openage::log
